# VD-02 data model
Cue: non-negative integer start_ms/end_ms, end strictly greater than start, Unicode text; sorted start, overlaps/repeated cues retained; maximum 100,000 cues.
Choices: non-empty exact language; precedence manual-first/auto-first/manual-only/auto-only; non-empty unique formats md/txt/json/srt/vtt; local_asr boolean default false.
Input: original URL, normalized target; discovery pending/scanning/complete/incomplete/failed; static reason; video keys. Reject credential-bearing input.
Video: hashed extractor+canonical ID key, source URL, title, input associations; disjoint status succeeded/caption_absent/inaccessible/failed/pending; reason, attempts; track language/kind/representation/acquisition; relative outputs/SHA256. No secret URLs or headers.
Batch: schema 1, inputs/choices, input records/video map/counts. Discovered equals sum of disjoint states. Attempted = records with attempts > 0. Exported = verified successes. Discovery independent from processing.
Cancel retains pending; resume verifies successes and rescans incomplete inputs. Retry failed only. OS file lock prevents concurrent mutation and releases on process exit; retained lock file does not block resume.
