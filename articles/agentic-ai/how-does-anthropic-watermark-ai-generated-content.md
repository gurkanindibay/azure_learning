---
type: Article
title: "How Does Anthropic Watermark AI-Generated Content?"
description: "How Anthropic and Google implement AI content watermarking and provenance using SynthID statistical token biasing and C2PA cryptographic content credentials to comply with EU AI Act Article 50, and their technical limitations against paraphrasing and metadata removal."
source: "https://pub.towardsai.net/how-anthropic-watermarks-ai-content-47265b651657"
author: "Dr. Leon Eversberg"
published: 2026-08-18
generated: { by: process:okf-migrate, at: 2026-08-26T00:00:00Z }
tags:
  - "clippings"
  - "ai-watermarking"
  - "synthid"
  - "c2pa"
  - "provenance"
---

# How Does Anthropic Watermark AI-Generated Content?

> **Source**: [Towards AI — Dr. Leon Eversberg](https://pub.towardsai.net/how-anthropic-watermarks-ai-content-47265b651657)  
> **Key Takeaways**: [39. AI Content Watermarking & Provenance Architectures](../../system-design-architecture/ai-ml-infrastructure/39-ai-key-takeaways.md)  
> **Dictionary**: [Generative Watermarking](../../reference-dictionary/ai-ml-llm.md#generative-watermarking), [Content Credentials (C2PA)](../../reference-dictionary/ai-ml-llm.md#content-credentials-c2pa), [G-Value (Watermark Scoring)](../../reference-dictionary/ai-ml-llm.md#g-value-watermark-scoring)

## Learn how AI watermarks are hidden in text and files, how they can be detected, and what happens when you try to remove them

![Python code snippet from the watermarks-remover tool that includes a prompt to paraphrase input text. This is used to weaken or remove statistical watermarks from text.](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*f5ZgvXdZBwuAE1Lz6-Mo7Q.png)

A simple prompt is all it takes to remove statistical watermarks from text. Code based on the tool watermarks-remover. Image by the author.

Anthropic recently announced that new Claude models will add invisible, machine-readable watermarks to AI-generated text and provenance metadata to generated images \[1\].

This comes as the EU AI Act’s transparency requirements take effect on August 2, 2026. According to Article 50 of the Act, providers of systems that generate or manipulate synthetic content must ensure their outputs are marked in a machine-readable format to allow for detection of artificial generation or manipulation \[2\].

To comply with this requirement, Anthropic and other major AI companies use a combination of imperceptible statistical watermarks and C2PA content credentials to record provenance information for generated files.

In this article, we will examine how these technologies operate, how statistical watermarks like **SynthID-Text** are embedded and detected, and how **C2PA** records the provenance of AI-generated files. Additionally, we will test what happens when watermarked text is paraphrased or translated, as well as whether C2PA metadata can be removed from an AI-generated image.

## How AI Text Watermarking Works

An LLM generates text one token at a time. At each generation step, the model has a probability distribution for the next possible tokens.

For instance, if the model generates “The quick brown fox,” possible next tokens could be “jumps,” “jumped,” “is,” and so on.

The watermark is **embedded** during the generation process. The sampling algorithm subtly changes the way it selects tokens, resulting in text with a **statistical signature**.

The important thing is that the generated text looks completely normal to a human reader.

![Diagram showing how SynthID-Text watermarks AI-generated text using a secret key, recent tokens, random seed, and sampling algorithm.](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*jpTzcQ8uxVwMLj_8LyD4UA.png)

The SynthID-Text generative watermarking scheme uses a random seed generator to influence the sampling algorithm. The random seed is based on the watermarking key and the most recent tokens from the context. Image by the author \[3\], content based on \[4\].

Developed by Google DeepMind \[4\], SynthID-Text uses a **secret watermarking key** and a sliding window of recently generated tokens to create a pseudo-random seed. The seed is then used to calculate watermark scores, or **g-values**, for candidate tokens.

The watermarking algorithm subtly favors tokens with higher g-values. This process is repeated for every generated token.

The result is text that appears normal but has a statistical bias toward tokens that received higher watermark scores.

This process does not insert a visible watermark. Rather, the watermark is hidden within the statistical properties of the token sequence.

## How AI Watermarks Are Detected

The second part of the watermarking process is detection.

A detector uses the tokenized text and the secret watermarking key as inputs. Using this information, it can reproduce the pseudo-random watermark scores for the tokens in the text. Access to the original LLM is not necessary for the detector.

![Diagram showing how SynthID detects AI-generated text using a watermarking key, scoring function, and threshold to classify text as watermarked or not watermarked.](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*CipZpxyMW71VA9ExkJUvWA.png)

Watermark detection with SynthID. Image by the author \[3\], content based on \[4\].

A simple approach to statistical watermark detection is to calculate the mean of all g-values.

For unwatermarked text, the g-values should be uniformly distributed. Therefore, the average will be **close to 0.5**.

However, for watermarked text, the sampling process introduces a positive bias, so the average score should be higher.

In summary, statistical watermark detection looks for patterns across many tokens. The signal is included in the tokens chosen to make up the text.

## How Accurate Are AI Text Watermarks?

Statistical watermarking is not perfect.

First, the AI model provider must embed the watermark. If a model does not implement watermarking, there is no corresponding watermark to detect. Additionally, the detector requires the appropriate watermarking configuration or must be trained for that configuration.

Second, longer texts provide stronger statistical evidence. Very short pieces of text contain fewer tokens, making it more difficult to distinguish a watermark signal from random variation.

Third, editing can affect the watermark. Since the watermark is related to the tokens selected during generation, changing those tokens weakens the signal.

Here’s what Anthropic has to say about text edits:

> **“Can’t someone just edit the text to get around the watermarking?**
> 
> To some extent, yes. Light editing probably won’t remove the watermark completely; a complete rewrite where every word is replaced will. In the latter case, of course, it’s arguable whether the text can any longer be described as AI-generated.” \[1\]

Two common transformations that weaken statistical watermarks are **paraphrasing** and **back-translation**.

Using a local `google/gemma-2b-it` LLM and the `transformers` library, I implemented my own SynthID watermarking and tested how the mean g-value changed when editing watermarked text \[3\].

- **Paraphrasing:** I used the *DeepL Write* AI tool to automatically rephrase the watermarked text from English to English.
- **Back-Translation:** I used the *Google Translate* AI tool for an English-to-Spanish-to-English translation.

The bar chart below shows the mean g-value scores from my small-scale experiment. Both paraphrasing and back-translation successfully reduced the watermark score.

![Bar chart comparing SynthID-Text watermark scores for watermarked, paraphrased, back-translated, and plain AI-generated text, showing how text editing weakens the watermark signal.](https://miro.medium.com/v2/resize:fit:1244/format:webp/0*bP_ZMiCQ_kSc5CVm.png)

Testing out the limitations of generative watermarking technologies. The watermarked and plain text were generated using google/gemma-2b-it with 300 tokens. Image created by the author in \[3\].

Therefore, a statistical watermark should not be interpreted as a perfect AI detector. Rather, it provides statistical evidence that a particular watermarking system may have been used in the generation process.

## C2PA Metadata Watermarking

There are several ways to record the origin of AI-generated content, one of which is statistical watermarking.

Another approach is the **C2PA Content Credentials** initiative. [C2PA](https://c2pa.org/) stands for the Coalition for Content Provenance and Authenticity. It is an open technical standard for recording the provenance of digital content.

Rather than altering the statistical properties of the generated content, C2PA adds a provenance record to the digital asset.

For example, an image generated by an AI system could contain the following information:

- The image was generated by an AI system.
- Which application or system created it.
- When it was created.
- Which actions were performed on the content afterward.

This information is stored in a **C2PA manifest**, also known as a **content credential**. A manifest can contain multiple assertions describing the asset’s provenance.

### Cryptographically Signed Metadata

C2PA verifies provenance information using **cryptographic signatures**. The basic idea is similar to that of a digitally signed document.

The creator or application signs the provenance information. Then, a C2PA-compatible system can verify the signature to determine if the information is authentic and if the content has been modified in a way that invalidates the record.

This establishes a chain of trust around the content.

### C2PA Manifest Example

For example, I used Google Gemini to generate an image of a cat. Then, I downloaded the file and verified it using a tool that inspects C2PA content credentials.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*J2baDZaT6meoxpqrX5uWrg.png)

A C2PA manifest example. I downloaded and then verified an AI-generated image from Google Gemini using https://c2paviewer.com/

The C2PA manifest provides information about the image’s provenance, including the system that created and processed the content.

More specifically, the manifest’s JSON data shows that Google Generative AI first created the image and subsequently applied an imperceptible SynthID-Image watermark.

If I were to edit the image using Adobe Photoshop, for example, additional information could be added to the content credentials describing that action.

## A Practical Watermark Removal Tool

On August 11, a new MIT-licensed open-source project called [**watermarks-remover**](https://github.com/guillaumemeyer/watermarks-remover) was released, just a few days before Anthropic’s announcement about adding watermarks. In just a few days, the project has already received over 10,000 stars on GitHub.

The tool can inspect files for invisible Unicode characters, rewrite text using LLMs to weaken statistical watermarks, and remove C2PA and other metadata from supported files.

### How to Remove or Bypass an AI Text Watermark

The tool performs text rewriting to remove or weaken statistical watermarks.

Examining the project’s source code reveals that the file `service/scripts/rewrite_text.py` uses common techniques, such as **paraphrasing** (the default setting) and **back-translation** (“English to French to English” by default):

```python
PROMPTS = {
    "paraphrase": (
        "Rewrite the following text so that it uses substantially different wording at "
        "the token level. Change clause order, connectors, and transition words; vary "
        "sentence boundaries and length; and replace both content words and function "
        "words where meaning allows. Preserve all facts, numbers, names, and technical "
        "identifiers. Do not add or remove claims. Output only the rewritten text.\n\n---\n{TEXT}"
    ),
    "humanize": (
        "Rewrite the following text so it reads as if a human wrote it from scratch. "
        "Vary sentence rhythm and length, replace formulaic AI-style transitions and "
        "filler with concrete natural phrasing, and use plain, varied wording. Preserve "
        "all facts, numbers, names, and technical identifiers. Do not add or remove "
        "claims. Output only the rewritten text.\n\n---\n{TEXT}"
    ),
    "code": (
        "Rewrite the natural-language parts of this code — comments, docstrings, and "
        "string literals — using different wording. Rename local variables, function "
        "parameters, and private helper names to semantically equivalent names. Preserve "
        "program behavior, public API names, and all values that affect output. Output "
        "only the rewritten code.\n\n---\n{TEXT}"
    ),
    "backtranslate_out": (
        "Translate the following text to {LANG}. Output only the translation.\n\n---\n{TEXT}"
    ),
    "backtranslate_back": (
        "Translate the following text to {ORIGINAL_LANG}. Preserve meaning; use natural "
        "phrasing. Output only the translation.\n\n---\n{TEXT}"
    ),
    "structural_outline": (
        "Extract a bullet outline of all claims and structure from the text "
        "(no full sentences). Output only the outline.\n\n---\n{TEXT}"
    ),
    "structural_write": (
        "Write a complete document from this outline in natural, varied human prose. "
        "Avoid formulaic transitions. Do not omit any bullet. Output only the document."
        "\n\n---\n{TEXT}"
    ),
}
```

### How to Remove C2PA Metadata

Using the C2PA manifest example image from above, I inspected the AI-generated image with `watermarks-remover`.

The output using the `service/scripts/inspect_image.py` is shown below:

```bash
python3 "$SCRIPTS/inspect_image.py" Gemini_Generated_Image_hg5is9hg5is9hg5i.jfif 
Path: Gemini_Generated_Image_hg5is9hg5is9hg5i.jfif
Format: jpeg
C2PA: True
AI metadata: True
Findings:
  - [confirmed] JPEG APP11 segment (JUMBF/C2PA common)
  - [confirmed] JPEG APP11: c2pa, C2PA, digitalSourceType, trainedAlgorithmicMedia, algorithmicMedia, SynthID, c2pa, C2PA
c2patool: no
exiftool: no
```

The tool correctly identified the C2PA metadata.

Then, we can remove the content credentials using `service/scripts/clean_image.py`:

```bash
python3 "$SCRIPTS/clean_image.py" Gemini_Generated_Image_hg5is9hg5is9hg5i.jfif -o Gemini_cleaned.jfif
wrote Gemini_cleaned.jfif (922224 -> 916198)
  - drop APP11 (C2PA/JUMBF)
  - preserved entropy-coded scan (SOS→EOF)
```

Finally, I verified the cleaned image using the same website as before. This time, however, the verification tool could not find any C2PA Content Credentials in the cleaned file.

![After using the watermarks-remover tool, the cleaned image now reads “No C2PA Data Found”.](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*cXLamzIF95uJlLUWCtdoxA.png)

This is a screenshot of the result of verifying the content credentials of the cleaned, AI-generated image from Google Gemini after using the watermarks-remover tool. Verification was done using https://c2paviewer.com/

## Conclusion

AI watermarking is not a single technology.

For text, statistical watermarking alters the probability of token selection during generation, resulting in text that contains a hidden statistical signal.

For images and other digital assets, provenance systems, such as C2PA, record information about the origin of the content and the modifications made to it.

These approaches solve different problems:

- A statistical watermark is part of the content itself. It can survive some forms of copying and editing, but large enough changes to the text will weaken the signal. The more the text changes, the weaker the signal becomes.
- C2PA, on the other hand, provides a cryptographically verifiable provenance record. It tells us what a participating system claims happened to a file. However, the metadata can be removed from formats that allow it to be stripped.

Therefore, neither technology should be considered a perfect AI detector. Using software such as the watermarks-remover tool, we can successfully remove or weaken these watermarks.

Consequently, text without a detectable watermark is not necessarily human-written. Likewise, an image without C2PA metadata is not necessarily human-created. However, watermarking systems provide additional evidence about how content was created.

## References

\[1\] Anthropic (2026), [How Claude’s text watermark works](https://www.anthropic.com/news/claude-text-watermark)

\[2\] EU Artificial Intelligence Act (2026), [Article 50: Transparency Obligations for Providers and Deployers of Certain AI Systems](https://artificialintelligenceact.eu/article/50/)

\[3\] [Dr. Leon Eversberg](https://medium.com/u/a67b10ad1762?source=post_page---user_mention--47265b651657---------------------------------------) (2026), [How To Detect AI-Generated Text with Google’s SynthID Watermarking](https://medium.com/generative-ai/detect-ai-generated-text-synthid-ca2874554374), *Generative AI*

\[4\] S. Dathathri and others (2024), [Scalable watermarking for identifying large language model outputs](https://www.nature.com/articles/s41586-024-08025-4), *Nature volume 634*
