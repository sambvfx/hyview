## Overview
`hyview` is a library for interacting with Houdini remotely. It provides a simple API for executing remote calls and ships with functionality for sending geometry points.

## Install Houdini
The apprentice version is available for free and comes with limited restrictions:

> Houdini Apprentice is a free version of Houdini FX which can be used by students, artists and hobbyists to create personal non-commercial projects. 

https://www.sidefx.com/products/houdini-apprentice/

## Build
```bash
git clone https://github.com/sambvfx/hyview.git
```

```bash
cd hyview
```

Make virtualenv for Houdini. This will create a `venv` folder inside the cloned directory.
```bash
bin/buildenv
```

Create your own virtualenv. Use Python 3 if you want!

```bash
virtualenv -p python3 venv3
```

Start Houdini from the launcher. You may have to update the launcher to point at your Houdini install location.

> TIP: You can set the environment variable `HOUDINI_CMD` to override the default the path to the houdini executable.

```bash
bin/launch_houdini
```

> TIP: Within Houdini, change to the `Technical` desktop to load a layout better suited to our needs.

In the `Python Shell` **within Houdini** type:

```python
import hyview
hyview.start_houdini()
```

This will start the server in Houdini we can interact with.

## Test

Start up another python process (which can be python 2/3) and send some test data to it to ensure it works:
```python
import hyview_samples.rand
hyview_samples.rand.sample()
```

## Basics

`hyview` is built around a few simple concepts.

- Simple interface
  - Data exchange utilizes abstract representations of Houdini data types. `hyview.Geometry` and `hyview.Point`
  - Bulid geometry in Houdini a point cloud by simply passing a `hyview.Geometry` object to `hyview.build`
  - Support for passing custom Houdini attributes. See `hyview.AttributeDefinition`.
- Aggressive and safe caching
  - By default results are cached to disk immediately for performace. Providing the same data twice will use the disk cache if one exists.
- Easy to extend with custom RPC methods.
  - Provides an easy way to execute remote commands in Houdini.

## Extending

You can provide your own RPC methods to call. For example:

```python
# mymodule.py

import hyview


@hyview.rpc()
def mesh_all():
    """
    Create a particle fliud mesh for all geo within the hyview root subnet.
    """
    import hyview.hy.core
    
    for node in hyview.hy.core.root().children():

        last = node.children()[-1]
        
        if 'particlefluidsurface' in last.type().name():
            # already meshed
            continue

        p = node.createNode('particlefluidsurface')
        p.parm('particlesep').set(8)
        p.parm('transferattribs').set('Cd')
        p.setInput(0, last)
        p.setDisplayFlag(True)
```
To ensure this RPC method is available in Houdini we need to make sure it's picked up by the server we start. There are a few ways to accomplish this:

When starting the server, optional path(s) can be provided which will be added to the RPC registry.

```python
import hyview
hyview.start_houdini('/path/to/mymodule.py')
```

Or set them as environment variables before you launch.
 
```bash
export HYVIEW_PLUGIN_PATH=/path/to/mymodule.py:/path/to/manypluginsdir
```

You can then call this procedure like you would normally (from another python session) - which will issue the RPC command to execute it remotely.

```python
import mymodule
mymodule.mesh_all()
```

Note you'll need to scope all Houdini specific imports.

## Samples

This repo contains a handful of samples to get you jump started. These are simple proof of concepts to illustrate how to use `hyview`.

> NOTE: Some of these samples require files to be downloaded and/or additional python packages to be installed.

#### Neuron

This is electron microscopy data and comes with a corresponding array of labels. Filtering to only specific labels provides some interesting results.

Download sample data from https://cremi.org/static/data/sample_A_20160501.hdf

Place the sample file in `./hyview_samples/_data`

> NOTE: You'll have to `pip install h5py` to load the data.

Use the helper to view something interesting!

```python
import hyview_samples.neuron
hyview_samples.neuron.sample()
```

#### Mitosis

This is fluorescence microscopy data over multiple time points. It's a 5D array with two channels (DNA and microtubules).

Download sample data from https://www.dropbox.com/s/dnq0ag1xbc6ft2u/mitosis.tif?dl=0

Place the sample file in `./hyview_samples/_data`

> NOTE: You'll have to `pip install scikit-image` to load the data.

Use the helper to view something interesting!

```python
import hyview_samples.mitosis
hyview_samples.mitosis.sample()
```