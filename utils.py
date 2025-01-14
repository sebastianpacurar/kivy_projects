import os
from functools import wraps
from threading import Thread

from kivy.clock import Clock
from kivy.properties import ListProperty


def wait_implicitly(callback):
    """
    Run the decorated function in a thread and execute the callback once it is finished \n
    Show global spinner during execution without blocking the main thread
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = {'data': None}  # store result from the thread

            def run_function():
                try:
                    # run the decorated function and store its result
                    res['data'] = func(*args, **kwargs)

                    # schedule the callback to execute in the main thread
                    Clock.schedule_once(lambda dt: callback(args[0], res['data']))

                finally:
                    # ensure the spinner is hidden after the function execution
                    Clock.schedule_once(lambda dt: args[0].app.hide_spinner())

            # show the spinner immediately
            Clock.schedule_once(lambda dt: args[0].app.show_spinner())

            # start the function in a thread
            Thread(target=run_function).start()

            # return nothing since it's non-blocking

        return wrapper

    return decorator


def find_project_root(target="README.md"):
    # go up x levels through directories until root is reached
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):  # go up one level iteratively
        if target in os.listdir(current_dir):
            return current_dir  # return directory if README.md is present
        current_dir = os.path.dirname(current_dir)  # go up one level


def rgb_format(rgb_val, factor=0.0, darken=False, lighten=False):
    """ Convert RGB from 0-255 range or 0.0-1.0 range and darken/lighten by the factor \n
        If factor is 0.0, then darken and lighten won't be taken into account \n
        If factor and both darken and lighten are True then throw value Error \n
        Does not have any alpha manipulation logic
    """
    float_rgb = []

    if isinstance(rgb_val, ListProperty):
        rgb_val = rgb_val.defaultvalue

    # check if it's already a float values list, else parse into float values
    if all(0 <= c <= 1 for c in rgb_val[:-1]):
        float_rgb = rgb_val[:-1]
    elif all(0 <= c <= 255 for c in rgb_val[:-1]):
        float_rgb = [c / 255 for c in rgb_val[:-1]]

    if not factor:
        # if no factor, return the float values
        float_rgb.append(rgb_val[-1] if rgb_val[-1] <= 1 else rgb_val[-1] / 255)
        return float_rgb
    else:
        if darken and lighten:
            raise ValueError(f"Cannot have darken and lighten set to True at the same time for {rgb_val} color")
        if darken:
            float_rgb = [max(0, c * (1 - factor)) for c in float_rgb]  # prevent from going under 0
        if lighten:
            float_rgb = [min(1, c + (1 - c) * factor) for c in float_rgb]  # prevent from going over 1

        float_rgb.append(rgb_val[-1] if rgb_val[-1] <= 1 else rgb_val[-1] / 255)  # add alpha back

    return float_rgb
