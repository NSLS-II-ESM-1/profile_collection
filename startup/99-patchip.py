from bluesky import Msg
from bluesky.plans import stage_decorator, separate_devices, run_decorator

def adaptive_scan(detectors, target_field, motor, start, stop,
                  min_step, max_step, target_delta, backstep,
                  threshold=0.8, *, md=None):
    """
    Scan over one variable with adaptively tuned step size.
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    target_field : string
        data field whose output is the focus of the adaptive tuning
    motor : object
        any 'setable' object (motor, temp controller, etc.)
    start : float
        starting position of motor
    stop : float
        ending position of motor
    min_step : float
        smallest step for fast-changing regions
    max_step : float
        largest step for slow-chaning regions
    target_delta : float
        desired fractional change in detector signal between steps
    backstep : bool
        whether backward steps are allowed -- this is concern with some motors
    threshold : float, optional
        threshold for going backward and rescanning a region, default is 0.8
    md : dict, optional
        metadata
    See Also
    --------
    :func:`bluesky.plans.relative_adaptive_scan`
    """
    _md = {'detectors': [det.name for det in detectors],
           'motors': [motor.name],
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'motor': repr(motor),
                         'start': start,
                         'stop': stop,
                         'min_step': min_step,
                         'max_step': max_step,
                         'target_delta': target_delta,
                         'backstep': backstep,
                         'threshold': threshold},
           'plan_name': 'adaptive_scan',
          }
    _md.update(md or {})

    @stage_decorator(list(detectors) + [motor])
    @run_decorator(md=_md)
    def adaptive_core():
        next_pos = start
        step = (max_step - min_step) / 2
        past_I = None
        cur_I = None
        cur_det = {}
        while next_pos < stop:
            yield Msg('checkpoint')
            yield Msg('set', motor, next_pos, group='A')
            yield Msg('wait', None, 'A')
            yield Msg('create', None, name='primary')
            for det in detectors:
                yield Msg('trigger', det, group='B')
            yield Msg('wait', None, 'B')
            for det in separate_devices(detectors + [motor]):
                cur_det = yield Msg('read', det)
                if cur_det is not None and target_field in cur_det:
                    cur_I = cur_det[target_field]['value']
            yield Msg('save')

            # special case first first loop
            if past_I is None:
                past_I = cur_I
                next_pos += step
                continue

            dI = np.abs(cur_I - past_I)

            slope = dI / step
            if slope:
                new_step = np.clip(target_delta / slope, min_step, max_step)
            else:
                new_step = np.min([step * 1.1, max_step])

            # if we over stepped, go back and try again
            if backstep and (new_step < step * threshold):
                next_pos -= step
                step = new_step
            else:
                past_I = cur_I
                step = 0.2 * new_step + 0.8 * step
            next_pos += step

    return (yield from adaptive_core())
