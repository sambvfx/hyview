## Install Houdini
Download Houdini. The Apprentice version is free and works just fine!:
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

> TIP: You can set the environment variable `HOUDINI_CMD` to specify your own 
application launcher.

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
import samples.rand
samples.rand.random_data()
```

## Basics

`hyview` is built around a few simple concepts.

- Simple interface
  - Abstract representations of houdini data types. `hyview.Geometry`, `hyview.Primitive` and `hyview.Point`
  - Build point cloud by simply passing a `hyview.Geometry` object to `hyview.build`
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
def mesh_all(names=None):
    """
    RPC method for "meshing" all geometry.

    Parameters
    ----------
    names : Optional[str]
    """
    import hyview.hy.core
    for node in hyview.hy.core.root().children():
        if names and node.name() not in names:
            continue
        last = node.children()[-1]
        p = node.createNode('particlefluidsurface')
        p.parm('particlesep').set(8)
        p.parm('transferattribs').set('Cd')
        p.setInput(0, last)
        p.setDisplayFlag(True)
```

To ensure this RPC method is available, we need to ensure it's found by the server running in Houdini. There are a few ways to accomplish this:

When starting the server, optional path(s) can be provided which will be added to the RPC registry.

```python
import hyview
hyview.start_houdini('/path/to/mymodule.py')
```

Or set them as environment variables before you launch.
 
```bash
export HYVIEW_PLUGIN_PATH=/path/to/mymodule.py:/path/to/manypluginsdir
```

With this set, you can call this procedure remotely like this:

```python
import mymodule
mymodule.mesh_all()
```

Note you'll need to scope all Houdini specific imports.

## Neuron Sample

Download sample data from https://cremi.org/static/data/sample_A_20160501.hdf
Place file in `./samples/_data`

> NOTE: You'll have to `pip install h5py` to load the data.

When starting Houdini server, include the `samples/neuron.py` path to ensure it registers the `mesh_all` rpc method.

```python
import hyview
hyview.start_houdini('~/projects/hyview/samples/neuron.py')
```

Generate some sample data.

```python
import samples.neuron
samples.neuron.build_interesting()
```