## Install Houdini
Download Houdini. The Apprentice version is free and works just fine!:
https://www.sidefx.com/products/houdini-apprentice/

Houdini comes with a python interpreter - which we often called `hython`. Currently Houdini follows the (VFX Reference Platform)[https://www.vfxplatform.com/] and utilizes python-2.7. This means hyview is required to run in both python2 and python3. 


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

Start up another python process (which can by python3) and send some test data to it to ensure it works:
```python
import samples.rand
samples.rand.random_data()
```

## Basics

`hyview` is built around a few simple concepts.

- Simple interface
  - Abstract representations of houdini data types. `hyview.Geometry`, `hyview.Primitive` and `hyview.Point`
  - Build point cloud by simply passing a `hyview.Geometry` object to `hyview.app().build`
  - Support for passing custom attributes. See `hyview.AttributeDefinition`.
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
def mesh_all(self, names=None):
    """
    RPC method for "meshing" all geometry.

    Parameters
    ----------
    self : hyview.hy.implementation.HoudiniApplicationController
    names : Optional[str]
    """
    for name, node in self.nodes.items():
        if names and name not in names:
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
export HYVIEW_PLUGIN_PATH=/path/to/mymodule.py:/path/to/manyplugins
```

With this set, you can simply call this with:

```python
import hyview
app = hyview.app()
app.mesh_all()
```