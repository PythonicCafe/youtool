import io


def vtt_to_string(vtt):
    result = io.StringIO()
    vtt.write(result)
    result.seek(0)
    return result.read()


def simplify_vtt(vtt):
    """Simplify VTT contents, removing per-word timings and deduplicating sentences

    `vtt` can be either `str` or `webvtt.WebVTT` instance
    """
    import webvtt  # noqa

    if isinstance(vtt, str):
        vtt = webvtt.read_buffer(io.StringIO(vtt))
    elif not isinstance(vtt, webvtt.WebVTT):
        raise TypeError(f"`vtt` must be instance of either `str` or `webvtt.WebVTT` (got: {type(vtt)})")
    simplified = []
    last_line = None
    for caption in vtt.captions:
        lines = caption.text.strip().splitlines()
        for line in lines:
            if not line:
                continue
            elif line == last_line:
                if simplified:
                    simplified[-1].end = caption.end
                continue
            simplified.append(webvtt.Caption(start=caption.start, end=caption.end, text=line))
            last_line = line
    # TODO: fix logic to have consecutive timings when simplifing YouTube automatic transcriptions - from
    # `tests/data/youtube-auto-hd-notebook.vtt`:
    # 00:07:14.000 00:07:19.150 perdido esses dados é isso espero que
    # 00:07:17.150 00:07:21.940 tenham gostado aí qualquer dúvida pode
    # 00:07:19.160 00:07:21.940 deixar nos comentários
    new_vtt = webvtt.WebVTT(captions=simplified)
    return vtt_to_string(new_vtt)
