# Running your first experiment (with Visiomode)

!!! note
    This is a work in progress. Please check back later for updates!

Now that we've built our arena, we can start running experiments with Visiomode. This guide will walk you through the process of running your first experiment with Visiomode, from setting up the touchscreen module to running a simple behavioural task.

!!! note
    This guide follows the protocol found in our [protocols.io repository](http://dx.doi.org/10.17504/protocols.io.bumgnu3w), which we described in [Eleftheriou et al. 2023](https://doi.org/10.1016/j.jneumeth.2022.109779). Here we will consider only the touchscreen-reward association task; you can refer to the [protocols.io repository](http://dx.doi.org/10.17504/protocols.io.bumgnu3w) for the full protocol, which extends to nose-poke and forelimb-reaching visual discrimination tasks.

## Setting up the touchscreen module

1. Power on the Raspberry Pi 4 and wait for the desktop to load. Make a note of the Pi's IP address, if this is not already known (see [the previous section](index.md)).

2. Connect to the raspberry pi via SSH.
    On Linux or MacOS, open a terminal and type the following. If you're on Windows, open a PowerShell terminal instead.
    ```bash
    ssh <YOUR-RPI-USERNAME>@<YOUR-IP-ADDRESS>
    ```
    Replacing `<YOUR-RPI-USERNAME>` & `<YOUR-IP-ADDRESS>` with the username you set when setting up the Raspberry Pi and the IP address you took note of in the previous step. You may be prompted for your password if you created one when setting up your Raspberry Pi.

3. Start the Visiomode server by running the following command:

    ```bash
    DISPLAY=:0 visiomode
    ```

4. Open a web browser on your computer and navigate to the following URL:

    ```bash
    http://<YOUR-IP-ADDRESS>:5000
    ```

    You should be greeted by Visiomode's web interface!

    ![Visiomode web interface](../assets/screengrabs/hello-visiomode.png)

5. Adjust the nose-poke perspex insert in front of the touchscreen.

6. (Optional) Adjust screen brightness.

7. Test the reward system by clicking the "Dispense reward" button on the web interface.

## Running your first experiment



## Cleaning up


## Next steps

