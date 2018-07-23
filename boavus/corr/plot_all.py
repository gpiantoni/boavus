
VALUE_TYPES = [
    'peak',
    'r2',
    ]


def plot_results(results_tsv, output_dir):
    img_dir = output_dir / PNG_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True)

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:
            fig = _plot_fit_over_kernel(one_tsv)
            output_png = img_dir / (one_tsv.stem + '.png')
            export_plotly(fig, output_png, driver=d)

        for value_type in VALUE_TYPES:
            for attribute in ATTRIBUTES:
                val_per_group, max_val = read_values_per_group(results_tsv,
                                                               attribute,
                                                               value_type)
                fig = _plot_histogram(val_per_group, max_val, attribute,
                                      value_type)
                output_png = img_dir / f'histogram_{attribute}_{value_type}.png'
                export_plotly(fig, output_png, driver=d)

