INSTRUCTIONS FOR RUNNING FROM THE SOURCE
----------------------------------------

1. Create a link called `meocloudd` in the `meocloud/client/linux/daemon/` folder, pointing to a `meocloudd` binary which can be found here:
  - If you already have meocloud installed in your machine, it should be in your installation folder (tipically it's `/opt/meocloud`).
  - If not, download the tar.gz version of meocloud from the url below, replacing `$ARCH` with your architecture (i386, x86_64, armv6l), `meocloudd` should be there too.

    URL: `https://meocloud.pt/binaries/linux/$ARCH/meocloud-latest_$ARCH_beta.tar.gz`

2. Create another link in `meocloud/client/linux/cli` called `daemon`, pointing to `meocloud/client/linux/daemon/daemon.py`.

3. Install `virtualenv` if you don't have it already.

4. Create a virtualenv for this project and activate it (although it's not required, you can also take a look at `virtualenvwrapper`).

5. Install the requirements for this project by running `pip install -r requirements.txt`.

6. Add the `meocloud` folder to your Python PATH. One easy way to do this is to create a link to the `meocloud` folder inside your `site-packages` folder in your virtualenv (you can get there easily if you installed `virtualenvwrapper` by running `cdsitepackages`)

7. Start MEO Cloud with `python meocloud/client/linux/cli/cli.py start`.

   NOTE: If you had MEO Cloud installed and running, this will be equivalent to running `meocloud start` which will fail since only one meocloud can be running at one time. Stop it first and try again.
