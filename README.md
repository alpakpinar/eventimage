# Event Image

A lightweight python package to plot 2D eta/phi images of events.

## Setup
This setup runs on `bucoffeaenv` environment. See bucoffea [setup instructions](https://github.com/bu-cms/bucoffea/wiki/Howto:-Setting-up-and-running-the-code) for information on setting up bucoffa environment.

## Running the code
The code can be executed with the `plot.py` script on the root directory. This script must be supplied with a path to an input ROOT file as it's first argument, and accepts a few more arguments:

* --tag: The tag for the current job. This will be used to set the name of the output directory.

* --jetsOnly: Use this flag to construct jet-based images (i.e. PF candidates **only** coming from jets.). If this flag is not specified, the image from **all** PF candidates will be used.

These two arguments are optional, and one can run the script as such:

```
./plot.py <input_root_file.root>
```
