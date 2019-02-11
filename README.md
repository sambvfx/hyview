Download Houdini:
https://www.sidefx.com/products/houdini-apprentice/

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

Start Houdini from the launcher. Update the launcher to point at your install.

```bash
bin/launch_houdini
```

Within Houdini, change to the `Technical` desktop via the menu bar. `Desktop -> Technical`.

In the `Python Shell` type:

```python
import hyview.hy
hyview.hy.start()
```

This will start the server in Houdini we can interact with.

Start up another python process and send some test data to it to ensure it works:
```python
import hyview.test
hyview.test.random_data()
```
