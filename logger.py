import logging

def setup_logging(debug=False):
    # Use modern {} formatting to avoid conflicts with % placeholders
    formatter = logging.Formatter("[{levelname}] {message}", style="{")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    log = logging.getLogger("RAG")
    log.handlers.clear()
    log.addHandler(handler)
    log.setLevel(logging.DEBUG if debug else logging.INFO)

    # Silence noisy libraries unless in debug mode
    noisy_libs = ["httpx", "httpcore", "urllib3"]
    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return log
