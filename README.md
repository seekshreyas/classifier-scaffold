classifier-scaffold
===================

My reusable code for using many different classifiers on a dataset.

It takes some command line flags, like:

```bash
$python appClassifierBenchmark.py --file="exports/appFeatures.csv" --classifier="all" --sample="split"
```

where,

- `--classifier`: takes inputs of what classifier we want to run. By default it runs all and takes key values of other models to specifically only run that model.
- `--sample`: takes inputs for whether we want to run the classifiers on all dataset, or equal splits. By default it takes all.
- `--help`: provides some output for the above help, but frankly it still needs a little improvement.


Save output from console to a file as:

```bash
$python appClassifierBenchmark.py --file="exports/appFeatures.csv" > <outputfile>
```
