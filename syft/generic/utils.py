from syft.generic.frameworks.attributes import allowed_commands
import syft as sy


class memorize(dict):
    """
    This is a decorator to cache a function output when the function is
    deterministic and the input space is small. In such condition, the
    function will be called many times to perform the same computation
    so we want this computation to be cached.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result


def allow_command(func):
    func_name = f"{func.__module__}.{func.__name__}"
    print("++++", func_name)
    allowed_commands.update({func_name})
    return func


def remote(func, location):
    command_name = f"{func.__module__}.{func.__name__}"

    worker = sy.local_worker

    if isinstance(location, str):
        location = worker.get_worker(location)

    def remote_exec(*args, return_value=False, return_arity=1, multiprocessing=False, **kwargs):

        response_ids = [sy.ID_PROVIDER.pop() for _ in range(return_arity)]

        command = (command_name, None, args, kwargs)

        response = worker.send_command(
            message=command, recipient=location, return_ids=response_ids, return_value=return_value
        )

        if multiprocessing:
            return response.get()
        else:
            return response

    return remote_exec
