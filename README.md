raspberrypi_python
==================

Clock/weather/bus display in office.  Use cron:

    */1 * * * * python ~pi/raspberrypi_python/update_localinfo.py -r -w --nobus -d /tmp/ -v; sudo chown pi /tmp/*.data; /usr/local/bin/scroll_ppm /tmp/localinfo.ppm 55
