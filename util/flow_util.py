import functools
import time

from util.display_util import highlight, clear

def get_validated_output(*, validation_func, prompt: str=None,
                         break_value: str=None, **kwargs):
    """Return a validated output of validation_func, or 'None' if loop is broken.

    @:param validation_func: (function) a validation function to return a valid output.
    Function should raise an exception upon an invalid input.
    @:param prompt: (str) a prompt to display for validation_func.
    If None given, no input will be asked.
    @:param break_value: (str) a value to break input loop upon encounter.
    """
    if prompt is not None:
        pr_suffix = highlight(' >>> ', color='g')
        prompt += pr_suffix
        def inner_action():
            inp = input(prompt)
            clear()
            if inp == break_value:
                return None
            else:
                return validation_func(inp, **kwargs)
    else:
        def inner_action():
            return validation_func(**kwargs)

    while True:
        try:
            return inner_action()
        except Exception as err:
            print(highlight(str(err).strip('\' '), color='r'))


def act_on_interrupt(func):
    """Decorate a function to go back on a keyboard interrupt.
     Single tap causes a restart, double tap causes an exit.
     """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                clear()
                try:
                    print(highlight('Press Ctrl + C again to quit...', 'r'))
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    exit()
                else:
                    continue
                finally:
                    clear()

    return wrapper
