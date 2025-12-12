# EPICC-builder
App to help you generate the sample file and config file for the epigeneticbutton pipeline.\
Link to github: [EPICC / epigeneticbutton](https://github.com/joncahn/epigeneticbutton)

[open EPICC-builder in streamlit](https://epicc-builder.streamlit.app/)

## Sample file
Fill the table with all your samples, following the template given. Each replicate should be a single row in the table. Hovering over the column headers return some directions. You can add rows by clicking on the + sign on the top right corner, and remove rows by checking the box on the leftmost column and clicking the bin in the top-right corner fo the table.\
Once your table is complete, click the epigenetic button to validate that your sample file is correct.\
If it is correct, you can download it at the bottom of the page!

## Config file
Fill in all the fields in the required parameters section. Output options and additional parameters can also be edited. These values will populate the config.yaml file used by snakemake, so make sure none are empty and they follow the same pattern than the default values.\
Once you have finished your selection, you can download your custom config file at the bottom of the page!

Note1: The config file will lose the comments and formatting from the original config file, and the original config file has more parameters that can be changed. For more control, edit it directly in unix (with vi for example).\
Note2: If you need to change the resources allocations, you will need to do that directly on the config file, or on the file in the `profiles` folder depending on the cluster manager you use.

## Click the button!
Once you have downloaded your two files, put them in the config folder of the epigeneticbutton repository you have cloned and start the pipeline! Refer to the epigenetic button README for how to launch it!
