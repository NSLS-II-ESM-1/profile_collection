import os
if os.getenv("BS_ENABLE_OLOG_CALLBACK", 1) == 1:
    from bluesky.callbacks.olog import logbook_cb_factory
    from functools import partial
    from pyOlog import SimpleOlogClient
    import queue
    import threading
    from warnings import warn
    import bluesky.callbacks.olog

    bluesky.callbacks.olog.TEMPLATES['long'] = """
    {{- start.plan_name }} ['{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})
    Scan Plan
    ---------
    {{ start.plan_name }}
    {% if 'plan_args' in start %}
        {%- for k, v in start.plan_args | dictsort %}
            {{ k }}: {{ v }}
        {%-  endfor %}
    {% endif %}
    {% if 'signature' in start -%}
    Call:
        {{ start.signature }}
    {% endif %}
    Metadata
    --------
    {% for k, v in start.items() -%}
    {%- if k not in ['plan_name', 'plan_args'] -%}{{ k }} : {{ v }}
    {% endif -%}
    {%- endfor -%}"""

    bluesky.callbacks.olog.TEMPLATES['desc'] = """
    {{- start.plan_name }} ['{{ start.uid[:6] }}'] (scan num: {{ start.scan_id }})"""

    bluesky.callbacks.olog.TEMPLATES['call'] = """RE({{ start.plan_name }}(
    {%- for k, v in start.plan_args.items() %}{%- if not loop.first %}   {% endif %}{{ k }}={{ v }}
    {%- if not loop.last %},
    {% endif %}{% endfor %}))
    """

    LOGBOOKS = ['Comissioning']  # list of logbook names to publish to

    # Set up the logbook. This configures bluesky's summaries of
    # data acquisition (scan type, ID, etc.).

    LOGBOOKS = ['Data Acquisition']  # list of logbook names to publish to
    simple_olog_client = SimpleOlogClient()
    generic_logbook_func = simple_olog_client.log
    configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

    # This is for ophyd.commands.get_logbook, which simply looks for
    # a variable called 'logbook' in the global IPython namespace.
    logbook = simple_olog_client

    cb = logbook_cb_factory(configured_logbook_func, desc_dispatch=desc_templates)



    def submit_to_olog(queue, cb):
        while True:
            name, doc = queue.get()  # waits until document is available
            try:
                cb(name, doc)
            except Exception as exc:
                warn('This olog is giving errors. This will not be logged.'
                     'Error:' + str(exc))

    olog_queue = queue.Queue(maxsize=100)
    olog_thread = threading.Thread(target=submit_to_olog, args=(olog_queue, cb), daemon=True)
    olog_thread.start()

    def send_to_olog_queue(name, doc):
        try:
            olog_queue.put((name, doc), block=False)
        except queue.Full:
            warn('The olog queue is full. This will not be logged.')

    RE.subscribe(send_to_olog_queue, 'start')
