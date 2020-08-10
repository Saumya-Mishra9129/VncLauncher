What is this?
=============

This activity helps you broadcast your screen to another computer. It will automatically launch a VNC server (X11vnc) and display your IP address. You can then connect and view the screen of Sugar on another conmputer using any VNC client (e.g. TigerVNC, UltraVNC Viewer, RealVNC, TightVNC etc).
 VncLauncher is not part of the Sugar desktop, but can be added.  Please refer to;

* [How to Get Sugar on sugarlabs.org](https://sugarlabs.org/),
* [How to use Sugar](https://help.sugarlabs.org/),

VncLauncher depends on Python, [Sugar
Toolkit](https://github.com/sugarlabs/sugar-toolkit-gtk3), GTK+ 3, Pango, Vte and x11vnc.


How to use?
===========

* Firstly, make sure your Sugar is connected to the wireless network or mesh network. You can also find the network information at the bottom of the screen inside Sugar.
* Select VncLauncher Activity to start the activity.
* Click at “Please Click to find the current IP address” to see your current IP address.
* VncLauncher depends on x11vnc, Please follow details given below _(How to install dependencies?)_ to install x11vnc. Also an alternate way to install x11vnc is to click OK ,which can be seen in dialog box after clicking on “Start X11 VNC Server”. Click “Start X11 VNC Server” to start your Sugar as a server so that your PC can connect to your Sugar.
* Click “Stop X11 VNC Server” or Exit VNC Launcher Activity, when you want to disconnect sugar from your PC. But “Exit VNC Launcher Activity” will close down the Activity. The Stop button will only stop connection and allow you to start the connection anytime. 
* In your PC, select the viewer program, Viewer programs which supports VncLauncher are TigerVNC, UltraVNC Viewer, RealVNC and TightVNC. You can also follow "_How to install vncviewer?_" to install RealVNC. 
* Enter your Sugar's ip address and click Connect. (Note***, Make sure your PC connect to the same network as the Sugar) .

How to install dependencies?
===========================================

Install the x11vnc

* Update the package index,
   - On Ubuntu/Debian systems, run
   ```sudo apt update```
   - On Fedora systems, run
   ```sudo dnf update```
* Install `x11vnc`,
   - On Ubuntu/Debian systems, run
    ```sudo apt install x11vnc```
   - On Fedora systems, run
    ```sudo dnf install x11vnc```
    
    
How to install vncviewer?
===========================================

Install RealVNC

* [Download VNC Viewer](https://www.realvnc.com/en/connect/download/viewer/linux/)
* Install the VNC Viewer program:
   - Open a Terminal.
   - Change directory to the download location, e.g. cd ~/Downloads
   - Run one of the following commands, depending on your version of Linux
       - ```sudo apt install ./<download-file>```    # Ubuntu/Debian
       - ```sudo yum install -y <download-file>```   # Fedora 
   - Sign in using your RealVNC account credentials. You should see the remote computer appear in your team.
   - Click or tap to connect. You are prompted to authenticate to VNC Server.

