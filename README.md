# OrangeSlices (WIP)

__WARNING: WORK IN PROGRESS__ It may kill your cat!

OrangeSlices is a python package/module to generate a statusline with
[LemonBar](https://github.com/LemonBoy/bar).


## Usage

Write a python script which loads the `orangeslices` package:

```python
import orangeslices as osl
```

Instatiate the `orangeslices.Orange` object and add the slices you want from `orangeslices.slices`:

```python
orange = osl.Orange()

clock = osl.slices.Clock()
orange.add(clock)
```

After that you call the `run()` method of your `orangeslices.Orange` to start LemonBar:

```python
orange.run()
```

See the [Examples](./examples) for a basic overview of the procedure. Or take a look at the 
[`orangeslices`](./orangeslices) and [`orangeslices.slices`](./orangeslices/slices) API documentation.


## Examples

__# TODO__


## TODO

- Add click handler to the slices

- Add multimonitor support

- Improve documentation

- Add more slices:

    - UPower

    - NetworkManager

    - Volume (PulseAudio / ALSA)

    - BSPWM Workspaces


## License

© 2016 Bernd Busse

OrangeSlices is licensed under the MIT license. For more information check [LICENSE](./LICENSE).
