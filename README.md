GIFted
======

A collector, organization, and search project for animated gifs.

Can't find the perfect animated gif for a situation?
----------------------------------------------------

This is because everything about the animated gif culture is organic,
chaotic and fun. The aim here is to collect these wonderful creations,
index them, tag them, and make them more generally useful beyond their
15 minutes of fame.

Development
-----------

1. Clone it
    ```git clone git@github.com:gmcquillan/gifted.git```
1. Setup Virtualenv
    ```virtualenv gifted```
1. Install requirements
    * ```cd gifted```
    * ```. bin/activate```
    * ```pip install -r requirements.txt```
1. Download some gifs!
```python collector.py```
  * Note: this will run every 30 minutes or so. Generally, just let it run for a few minutes and you'll have a few dozen gifs.
1. Startup Development Web Service
``` python web.py```
1. Browse to service: [http://localhost:5000/](http://localhost:5000)
