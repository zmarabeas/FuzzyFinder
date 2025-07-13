from backend.task_queue import enqueue, get_status, start_background_worker
import time

start_background_worker()

def test_enqueue_and_status():
    job_id = enqueue(lambda: time.sleep(0.05))
    assert get_status(job_id) in ('queued', 'running', 'completed')
    # Wait for completion
    time.sleep(0.1)
    assert get_status(job_id) == 'completed'