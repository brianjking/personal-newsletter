def sliding_window(text, window_size, overlap_size):
    tokens = text.split()
    windows = []
    start = 0
    end = window_size

    while end < len(tokens):
        windows.append(" ".join(tokens[start:end]))
        start += window_size - overlap_size
        end += window_size - overlap_size

    windows.append(" ".join(tokens[start:]))
    return windows

def process_windows(windows, model, prompt_template):
    summaries = []

    for window in windows:
        prompt = prompt_template.format(text=window)
        summary = model.generate(prompt)
        summaries.append(summary)

    return summaries

def combine_summaries(summaries, overlap_size):
    combined_summary = summaries[0]

    for summary in summaries[1:]:
        combined_summary += " " + " ".join(summary.split()[overlap_size:])

    return combined_summary
