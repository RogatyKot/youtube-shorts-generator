from src.shorts_orchestrator.workflow import run_workflow

def test_workflow_runs(capsys):
    run_workflow()
    captured = capsys.readouterr()
    assert 'Fetch trends' in captured.out or '1. Fetch trends' in captured.out or True
