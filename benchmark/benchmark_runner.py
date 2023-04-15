import timeit
import importlib


def run_benchmarks(module):
    benchmark_results = {}

    for name in dir(module):
        if name.startswith('benchmark'):
            benchmark_func = getattr(module, name)
            if callable(benchmark_func):
                timer = timeit.Timer(benchmark_func)
                result = timer.timeit(number=1)  # Change the number of iterations if needed
                benchmark_results[name] = result

    return benchmark_results


if __name__ == '__main__':
    results = run_benchmarks('benchmark')
    for name, result in results.items():
        print(f"{name}: {result:.4f} seconds")
