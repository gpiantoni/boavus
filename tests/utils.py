from json import load, dump


def update_parameters(PARAMETERS_JSON, **kwargs):
    if PARAMETERS_JSON.exists():
        with PARAMETERS_JSON.open() as f:
            PARAMETERS = load(f)

        PARAMETERS.update(kwargs)

    else:
        PARAMETERS = kwargs

    with PARAMETERS_JSON.open('w') as f:
        dump(PARAMETERS, f, indent='  ')
