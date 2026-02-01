import concurrent.futures
from typing import Callable, List, Any

class ParallelExecutor:
    @staticmethod
    def execute(tasks: List[Callable[[], Any]], max_workers: int = 3) -> List[Any]:
        """
        Executes a list of callables in parallel.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(task): task for task in tasks}
            for future in concurrent.futures.as_completed(future_to_task):
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    print(f'Task generated an exception: {exc}')
                    results.append({"error": str(exc)})
        return results
