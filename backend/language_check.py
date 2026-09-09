from langdetect import detect,DetectorFactory,LangDetectException
DetectorFactory.seed=0
def check_answer_language(answer,language):
    # Check prose separately; names, URLs and JSON keys must not influence detection.
    blocks=[p['text'] for p in answer['paragraphs']]+[answer.get('limitations','')]
    for text in blocks:
        if len(text.strip())<45:continue
        try:found=detect(text)
        except LangDetectException:raise ValueError('Cannot verify answer language') from None
        if found!=language:raise ValueError('Answer language does not match selection')
