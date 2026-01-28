# features/environment.py
import traceback

def after_step(context, step):
    """Capture full traceback on step failure."""
    if step.status == "failed":
        print("\n" + "="*70)
        print(f"FAILED: {step.keyword} {step.name}")
        traceback.print_exception(
            type(step.exception),
            step.exception,
            step.exception.__traceback__
        )
        print("="*70 + "\n")