import { useState, useCallback, useEffect, useRef } from "react";
const API = import.meta.env.VITE_API_URL || "";

const LANGUAGES = {
  en: "English", ga: "Irish (Gaeilge)", pl: "Polish", ro: "Romanian",
  pt: "Portuguese", es: "Spanish", fr: "French", de: "German",
  it: "Italian", ar: "Arabic", hi: "Hindi", ur: "Urdu",
  zh: "Chinese", fil: "Filipino", lt: "Lithuanian", lv: "Latvian",
  uk: "Ukrainian", ru: "Russian", cs: "Czech", sk: "Slovak",
  hu: "Hungarian", bg: "Bulgarian", hr: "Croatian"
};

const DOC_ICONS = {
  Revenue_notice: "€", Revenue_assessment: "€",
  HAP_form: "⌂", PPS_application: "ID",
  DSP_letter: "§", visa_application: "✈",
  visa_refusal: "✗", HSE_letter: "+",
  employment_permit: "W", eviction_notice: "!",
  debt_collection: "€", utility_bill: "⚡", unknown: "?"
};

const PRIORITY_CONFIG = {
  high:   { label: "HIGH",   bg: "#fff5f5", border: "#d93025", text: "#b71c1c" },
  medium: { label: "MED",    bg: "#fffbf0", border: "#e08c00", text: "#8a5c00" },
  low:    { label: "LOW",    bg: "#f4fbf7", border: "#1a7f4b", text: "#1a7f4b" },
};

function TypewriterText({ text, delay = 0, speed = 42, onDone }) {
  const [displayed, setDisplayed] = useState("");
  const [started, setStarted] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setStarted(true), delay);
    return () => clearTimeout(t);
  }, [delay]);
  useEffect(() => {
    if (!started) return;
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(iv); onDone?.(); }
    }, speed);
    return () => clearInterval(iv);
  }, [started]);
  return (
    <span>
      {displayed}
      <span style={{ opacity: displayed.length < text.length ? 1 : 0, borderRight: "3px solid #111", marginLeft: 1 }}>&nbsp;</span>
    </span>
  );
}

function HeroSection({ onStart }) {
  const [phase, setPhase] = useState(0);
  useEffect(() => { setPhase(0); }, []);
  return (
    <section style={s.hero}>
      <div style={s.heroInner}>
        <div style={s.heroLeft}>
          <p style={s.heroEyebrow}>AI · Ireland · 23 Languages</p>
          <h1 style={s.heroH1}>
            <span style={s.heroLineGray}>
              {phase >= 0 && (
                <TypewriterText text="Stop fearing" delay={500} speed={60} onDone={() => setPhase(1)} />
              )}
            </span>
            <br />
            <span style={s.heroLineGray}>
              {phase >= 1 && (
                <TypewriterText text="official letters." delay={100} speed={60} onDone={() => setPhase(2)} />
              )}
            </span>
            <br />
            <span style={{
              ...s.heroLineGreen,
              opacity: phase >= 2 ? 1 : 0,
              transform: phase >= 2 ? "translateY(0)" : "translateY(12px)",
              transition: "opacity 0.9s ease 1.2s, transform 0.9s ease 1.2s",
            }}>
              We explain them.
            </span>
          </h1>
          <p style={{ ...s.heroBody, opacity: phase >= 2 ? 1 : 0, transition: "opacity 0.8s ease 2s" }}>
            Upload any Irish government document — Revenue notices, HAP forms,
            visa decisions, DSP letters. Get a plain-English explanation, action
            steps, and a drafted response letter. In your language.
          </p>
          <div style={{ ...s.heroCtas, opacity: phase >= 2 ? 1 : 0, transition: "opacity 0.7s ease 2.4s" }}>
            <button style={s.ctaBtn} onClick={onStart}>Upload a document</button>
            <div style={s.pillRow}>
              {["23 languages", "Revenue · HAP · DSP · Visa", "Plain English"].map((p) => (
                <span key={p} style={s.pill}>{p}</span>
              ))}
            </div>
          </div>
        </div>
        <div style={s.heroRight}>
          <img src="/hero.png" alt="Bureaucracy Destroyer" style={{
            ...s.heroImg,
            opacity: phase >= 2 ? 1 : 0,
            transition: "opacity 1.4s ease 2.8s",
          }} />
        </div>
      </div>
    </section>
  );
}

function StepIndicator({ current }) {
  const steps = ["Upload", "Analyse", "Results"];
  return (
    <div style={s.stepIndicator}>
      {steps.map((label, i) => (
        <div key={label} style={s.stepItem}>
          <div style={{
            ...s.stepDot,
            background: i <= ["upload","analyse","results"].indexOf(current) ? "#1a7f4b" : "#ddd",
          }} />
          <span style={{
            ...s.stepLabel,
            color: i === ["upload","analyse","results"].indexOf(current) ? "#1a7f4b" : "#aaa",
            fontWeight: i === ["upload","analyse","results"].indexOf(current) ? 600 : 400,
          }}>{label}</span>
          {i < 2 && <div style={s.stepLine} />}
        </div>
      ))}
    </div>
  );
}

function UploadStage({ onUploaded }) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [lang, setLang] = useState("auto");

  const handleFile = useCallback(async (file) => {
    if (!file) return;
    setError(""); setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      if (!res.ok) throw new Error();
      const data = await res.json();
      onUploaded(data, lang);
    } catch {
      setError("Upload failed — make sure the API is running.");
    } finally { setUploading(false); }
  }, [lang, onUploaded]);

  return (
    <div style={s.stageCard}>
      <StepIndicator current="upload" />
      <h2 style={s.stageTitle}>Upload your document</h2>
      <p style={s.stageSub}>PDF or photo — any Irish government document</p>
      {error && <div style={s.errorBar}>{error}</div>}
      <div
        style={{ ...s.dropzone, ...(dragOver ? s.dropzoneHover : {}) }}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
      >
        {uploading ? (
          <div style={s.loadingState}>
            <div style={s.spinner} />
            <p style={s.loadingText}>Extracting text with AWS Textract...</p>
          </div>
        ) : (
          <>
            <div style={s.uploadIcon}>
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1a7f4b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="12" y1="18" x2="12" y2="12"/>
                <polyline points="9,15 12,12 15,15"/>
              </svg>
            </div>
            <p style={s.dropTitle}>Drag and drop here</p>
            <p style={s.dropSub}>PDF · JPG · PNG · TIFF</p>
            <label style={s.fileBtn}>
              Choose file
              <input type="file" accept=".pdf,.jpg,.jpeg,.png,.tiff,.bmp" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
            </label>
          </>
        )}
      </div>
      <div style={s.formRow}>
        <label style={s.formLabel}>Response language</label>
        <select value={lang} onChange={(e) => setLang(e.target.value)} style={s.select}>
          <option value="auto">Auto-detect</option>
          {Object.entries(LANGUAGES).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
        </select>
      </div>
      <div style={s.docTagsRow}>
        {["Revenue Notice", "HAP Form", "PPS Letter", "DSP Letter", "Visa Decision", "Utility Bill", "HSE Letter"].map((d) => (
          <span key={d} style={s.docTag}>{d}</span>
        ))}
      </div>
    </div>
  );
}

function AnalyseStage({ uploadResult, lang, onAnalysed }) {
  const [situation, setSituation] = useState("");
  const [analysing, setAnalysing] = useState(false);
  const [error, setError] = useState("");
  const [selectedLang, setSelectedLang] = useState(lang);

  const handleAnalyse = async () => {
    setError(""); setAnalysing(true);
    try {
      const res = await fetch(`${API}/analyse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: uploadResult.document_id,
          target_language: selectedLang,
          user_situation: situation,
        }),
      });
      if (!res.ok) throw new Error();
      onAnalysed(await res.json());
    } catch { setError("Analysis failed — please try again."); }
    finally { setAnalysing(false); }
  };

  return (
    <div style={s.stageCard}>
      <StepIndicator current="analyse" />
      <h2 style={s.stageTitle}>Review and analyse</h2>
      <p style={s.stageSub}>Confirm your document, then let Claude analyse it</p>
      {error && <div style={s.errorBar}>{error}</div>}
      <div style={s.uploadedBadge}>
        <div style={s.uploadedIconBox}>{DOC_ICONS[uploadResult.doc_type] || "?"}</div>
        <div style={s.uploadedInfo}>
          <div style={s.uploadedType}>{uploadResult.doc_type?.replace(/_/g, " ")}</div>
          <div style={s.uploadedMeta}>{uploadResult.ocr_source} · {LANGUAGES[uploadResult.detected_language] || "English"}</div>
        </div>
        <span style={s.checkmark}>✓ Uploaded</span>
      </div>
      <div style={s.previewBox}>
        <p style={s.previewLabel}>Extracted text preview</p>
        <p style={s.previewText}>{uploadResult.text_preview}...</p>
      </div>
      <div style={s.formGroup}>
        <label style={s.formLabel}>
          Your situation <span style={s.optionalTag}>optional but recommended</span>
        </label>
        <textarea
          style={s.textarea}
          placeholder="e.g. I am an immigrant living in Dublin and cannot afford to pay this amount in full by the deadline..."
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          rows={3}
        />
        <p style={s.fieldHint}>Adding your situation helps Claude draft a personalised response letter.</p>
      </div>
      <div style={s.formRow}>
        <label style={s.formLabel}>Explain in</label>
        <select value={selectedLang} onChange={(e) => setSelectedLang(e.target.value)} style={s.select}>
          <option value="auto">Auto-detect ({LANGUAGES[uploadResult.detected_language] || "English"})</option>
          {Object.entries(LANGUAGES).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
        </select>
      </div>
      <button onClick={handleAnalyse} disabled={analysing} style={analysing ? s.btnGhost : s.btnPrimary}>
        {analysing
          ? <span style={s.btnRow}><span style={s.spinnerWhite} /> Analysing with Claude AI...</span>
          : "Analyse document"}
      </button>
    </div>
  );
}

function ResultsStage({ analysis, onReset }) {
  const [data, setData] = useState(analysis);
  const [translateLang, setTranslateLang] = useState("pl");
  const [translating, setTranslating] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleTranslate = async () => {
    setTranslating(true);
    try {
      const res = await fetch(`${API}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: data.analysis_id, target_language: translateLang }),
      });
      if (!res.ok) throw new Error();
      const d = await res.json();
      setData(prev => ({ ...prev, ...d }));
    } catch {}
    finally { setTranslating(false); }
  };

  const copy = () => {
    navigator.clipboard.writeText(data.drafted_letter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadPDF = () => {
    const content = data.drafted_letter;
    const docType = data.doc_type?.replace(/_/g, " ") || "Document";
    const blob = new Blob([
      `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Response Letter - ${docType}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Lato:wght@300;400;700&display=swap');
  body { font-family: 'Lato', sans-serif; font-size: 12pt; line-height: 1.8; margin: 60px; color: #000; }
  h2 { font-family: 'Bebas Neue', sans-serif; font-size: 28pt; letter-spacing: 0.06em; margin-bottom: 4px; color: #1a7f4b; }
  .meta { font-size: 10pt; color: #666; margin-bottom: 40px; border-bottom: 1px solid #e0e0e0; padding-bottom: 16px; }
  pre { white-space: pre-wrap; font-family: 'Lato', sans-serif; font-size: 12pt; line-height: 1.8; }
  .warning { background: #fffbf0; border: 1px solid #ffe4a0; border-radius: 6px; padding: 10px 14px; font-size: 10pt; color: #888; margin-bottom: 32px; }
  .footer { margin-top: 60px; font-size: 9pt; color: #999; border-top: 1px solid #ccc; padding-top: 10px; }
</style>
</head>
<body>
<h2>STOP FEARING THIS LETTER</h2>
<div class="meta">Response to: ${docType} &nbsp;·&nbsp; Generated by Bureaucracy Destroyer · bureaucracy-destroyer.vercel.app</div>
<div class="warning">⚠️ Fill in all [PLACEHOLDERS] with your personal details before sending this letter.</div>
<pre>${content}</pre>
<div class="footer">Keep a copy for your records. Generated by Bureaucracy Destroyer.</div>
</body>
</html>`
    ], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `response-letter-${docType.replace(/\s+/g, '-').toLowerCase()}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={s.stageCard}>
      <StepIndicator current="results" />
      <div style={s.resultsTop}>
        <div style={s.resultsDocRow}>
          <div style={s.resultsIconBox}>{DOC_ICONS[data.doc_type] || "?"}</div>
          <div>
            <h2 style={s.resultsDocName}>{data.doc_type?.replace(/_/g, " ")}</h2>
            <p style={s.resultsDocMeta}>
              {LANGUAGES[data.detected_language] || "English"} &nbsp;·&nbsp;
              {Math.round((data.confidence_score || 0) * 100)}% confidence
            </p>
          </div>
        </div>
        <button onClick={onReset} style={s.newBtn}>+ New document</button>
      </div>

      {/* Explanation */}
      <div style={s.section}>
        <p style={s.sectionLabel}>Explanation</p>
        <p style={s.explanation}>{data.explanation}</p>
      </div>

      {/* Action Steps */}
      {data.action_steps?.length > 0 && (
        <div style={s.section}>
          <p style={s.sectionLabel}>What you need to do</p>
          <div style={s.stepsList}>
            {data.action_steps.map((step, i) => {
              const p = PRIORITY_CONFIG[step.priority] || PRIORITY_CONFIG.medium;
              return (
                <div key={i} style={{ ...s.stepCard, borderLeftColor: p.border, background: p.bg }}>
                  <div style={s.stepHeader}>
                    <span style={{ ...s.stepNum, background: p.border }}>Step {step.step}</span>
                    <span style={{ ...s.priorityBadge, color: p.text, borderColor: p.border }}>{p.label}</span>
                    {step.deadline && <span style={s.deadlineChip}>⏱ {step.deadline}</span>}
                  </div>
                  <p style={s.stepText}>{step.action}</p>
                  {step.link && (
                    <a href={step.link} target="_blank" rel="noreferrer" style={s.stepLink}>
                      {step.link} →
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Deadlines */}
      {data.extracted_deadlines?.length > 0 && (
        <div style={s.section}>
          <p style={s.sectionLabel}>Key deadlines</p>
          <div style={s.deadlinesList}>
            {data.extracted_deadlines.map((d, i) => (
              <div key={i} style={s.deadlineCard}>
                <span style={s.deadlineDate}>{d.date || "TBD"}</span>
                <span style={s.deadlineDesc}>{d.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Letter — redesigned */}
      {data.drafted_letter && (
        <div style={s.letterSection}>
          <div style={s.letterHeader}>
            <div style={s.letterTitleRow}>
              <span style={s.letterIcon}>📄</span>
              <div style={{ flex: 1 }}>
                <p style={s.letterTitle}>STOP FEARING THIS LETTER</p>
                <p style={s.letterSubtitle}>Your personalised response — ready to print and post</p>
              </div>
              <span style={s.importantBadge}>ACTION REQUIRED</span>
            </div>
            <div style={s.letterWarning}>
              ⚠️ Fill in all <strong>[PLACEHOLDERS]</strong> with your personal details before sending.
            </div>
          </div>
          <pre style={s.letterBody}>{data.drafted_letter}</pre>
          <div style={s.letterActions}>
            <button onClick={copy} style={s.letterCopyBtn}>
              {copied ? "✓ Copied" : "📋 Copy Letter"}
            </button>
            <button onClick={downloadPDF} style={s.letterPdfBtn}>
              📥 Download as PDF
            </button>
          </div>
        </div>
      )}

      {/* Translate */}
      <div style={s.section}>
        <p style={s.sectionLabel}>Translate to another language</p>
        <div style={s.translateRow}>
          <select value={translateLang} onChange={(e) => setTranslateLang(e.target.value)} style={{ ...s.select, flex: 1 }}>
            {Object.entries(LANGUAGES).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
          </select>
          <button onClick={handleTranslate} disabled={translating} style={translating ? s.btnGhost : s.btnPrimary}>
            {translating ? "Translating..." : "Translate"}
          </button>
        </div>
      </div>

      <button onClick={onReset} style={s.outlineBtn}>+ Analyse another document</button>
    </div>
  );
}

export default function App() {
  const [stage, setStage] = useState("home");
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadLang, setUploadLang] = useState("auto");
  const [analysis, setAnalysis] = useState(null);
  const appRef = useRef(null);

  const goToUpload = () => {
    setStage("upload");
    setTimeout(() => appRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
  };

  return (
    <div style={s.root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Lato:wght@300;400;700&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #f7f7f5; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        ::selection { background: #1a7f4b22; }
        textarea:focus, select:focus { outline: 2px solid #1a7f4b; outline-offset: 0; }
      `}</style>

      {/* NAV */}
      <nav style={s.nav}>
        <div style={s.navInner}>
          <div style={s.navLogo} onClick={() => setStage("home")} role="button">
            <img src="/logo.png" alt="logo" style={s.navLogoImg} />
            <span style={s.navBrand}>Bureaucracy <span style={s.navGreen}>Destroyer</span></span>
          </div>
          <div style={s.navRight}>
            <span style={s.navFlag}>🇮🇪 Ireland</span>
            <button style={s.navBtn} onClick={goToUpload}>Try it free</button>
          </div>
        </div>
      </nav>

      {/* HERO */}
      {stage === "home" && <HeroSection onStart={goToUpload} />}

      {/* HOW IT WORKS */}
      {stage === "home" && (
        <section style={s.howSection}>
          <div style={s.howInner}>
            <p style={s.howEyebrow}>How it works</p>
            <div style={s.howGrid}>
              {[
                { n: "01", title: "Upload", body: "Drop a PDF or photo of any Irish government document." },
                { n: "02", title: "AI Analyses", body: "Claude reads, classifies, extracts deadlines and action steps." },
                { n: "03", title: "You Act", body: "Get a plain-English explanation, a drafted letter, and WhatsApp reminders." },
              ].map((item) => (
                <div key={item.n} style={s.howCard}>
                  <p style={s.howNum}>{item.n}</p>
                  <p style={s.howTitle}>{item.title}</p>
                  <p style={s.howBody}>{item.body}</p>
                </div>
              ))}
            </div>
            <div style={s.howCta}>
              <button style={s.btnPrimary} onClick={goToUpload}>Upload your first document</button>
            </div>
          </div>
        </section>
      )}

      {/* APP STAGES */}
      <div ref={appRef} style={s.appWrap}>
        {stage === "upload" && (
          <UploadStage onUploaded={(data, lang) => { setUploadResult(data); setUploadLang(lang); setStage("analyse"); }} />
        )}
        {stage === "analyse" && uploadResult && (
          <AnalyseStage
            uploadResult={uploadResult}
            lang={uploadLang}
            onAnalysed={(data) => { setAnalysis(data); setStage("results"); }}
          />
        )}
        {stage === "results" && analysis && (
          <ResultsStage
            analysis={analysis}
            onReset={() => { setStage("upload"); setUploadResult(null); setAnalysis(null); }}
          />
        )}
      </div>

      {/* FOOTER */}
      <footer style={s.footer}>
        <div style={s.footerInner}>
          <div style={s.footerLeft}>
            <img src="/logo.png" alt="logo" style={{ width: 24, height: 24, objectFit: "contain" }} />
            <span style={s.footerBrand}>Bureaucracy Destroyer</span>
          </div>
          <p style={s.footerRight}>Claude AI · AWS Textract · pgvector · FastAPI · Ireland 🇮🇪</p>
        </div>
      </footer>
    </div>
  );
}

const s = {
  root: { minHeight: "100vh", background: "#f7f7f5", fontFamily: "'Lato', sans-serif", color: "#1a1a1a" },

  nav: { background: "#fff", borderBottom: "1px solid #e8e8e4", position: "sticky", top: 0, zIndex: 100 },
  navInner: { maxWidth: 1120, margin: "0 auto", padding: "0 24px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" },
  navLogo: { display: "flex", alignItems: "center", gap: 10, cursor: "pointer" },
  navLogoImg: { width: 32, height: 32, objectFit: "contain" },
  navBrand: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 22, letterSpacing: "0.04em", color: "#1a1a1a" },
  navGreen: { color: "#1a7f4b" },
  navRight: { display: "flex", alignItems: "center", gap: 20 },
  navFlag: { fontSize: 13, color: "#888", fontWeight: 400 },
  navBtn: { background: "#1a7f4b", color: "#fff", border: "none", borderRadius: 6, padding: "9px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer", letterSpacing: "0.01em" },

  hero: { background: "#fff", borderBottom: "1px solid #e8e8e4" },
  heroInner: { maxWidth: 1120, margin: "0 auto", padding: "64px 24px 0", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 48, alignItems: "center" },
  heroLeft: { paddingBottom: 64 },
  heroEyebrow: { fontFamily: "'Lato', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: "0.2em", color: "#1a7f4b", textTransform: "uppercase", marginBottom: 24 },
  heroH1: { fontFamily: "'Bebas Neue', sans-serif", fontSize: "clamp(52px, 6vw, 86px)", lineHeight: 0.96, letterSpacing: "0.02em", marginBottom: 28 },
  heroLineGray: { color: "#1a1a1a" },
  heroLineGreen: { color: "#1a7f4b", display: "inline-block" },
  heroBody: { fontSize: 16, lineHeight: 1.75, color: "#555", marginBottom: 36, maxWidth: 460, fontWeight: 300 },
  heroCtas: { display: "flex", flexDirection: "column", gap: 20 },
  ctaBtn: { display: "inline-block", width: "fit-content", background: "#1a7f4b", color: "#fff", border: "none", borderRadius: 6, padding: "14px 32px", fontSize: 15, fontWeight: 700, cursor: "pointer", letterSpacing: "0.01em" },
  pillRow: { display: "flex", flexWrap: "wrap", gap: 8 },
  pill: { background: "#f0f0ec", borderRadius: 20, padding: "5px 14px", fontSize: 12, color: "#555", fontWeight: 400 },
  heroRight: { display: "flex", justifyContent: "center", alignItems: "flex-end" },
  heroImg: { width: "100%", maxWidth: 520, objectFit: "contain", opacity: 0, transition: "opacity 1.2s ease" },

  howSection: { background: "#f7f7f5", borderBottom: "1px solid #e8e8e4" },
  howInner: { maxWidth: 1120, margin: "0 auto", padding: "72px 24px" },
  howEyebrow: { fontSize: 11, fontWeight: 700, letterSpacing: "0.2em", textTransform: "uppercase", color: "#888", marginBottom: 40, textAlign: "center" },
  howGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 24, marginBottom: 48 },
  howCard: { background: "#fff", borderRadius: 12, padding: "28px 24px", border: "1px solid #e8e8e4" },
  howNum: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 32, color: "#1a7f4b", letterSpacing: "0.04em", marginBottom: 8 },
  howTitle: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 22, letterSpacing: "0.03em", marginBottom: 10, color: "#1a1a1a" },
  howBody: { fontSize: 14, color: "#666", lineHeight: 1.65, fontWeight: 300 },
  howCta: { textAlign: "center" },

  appWrap: { maxWidth: 680, margin: "0 auto", padding: "48px 24px 64px" },
  stageCard: { background: "#fff", borderRadius: 16, padding: "36px 32px", border: "1px solid #e8e8e4", animation: "fadeUp 0.35s ease" },

  stepIndicator: { display: "flex", alignItems: "center", marginBottom: 28 },
  stepItem: { display: "flex", alignItems: "center", gap: 6 },
  stepDot: { width: 10, height: 10, borderRadius: "50%", flexShrink: 0, transition: "background 0.3s" },
  stepLabel: { fontSize: 12, transition: "color 0.3s" },
  stepLine: { width: 32, height: 1, background: "#e0e0d8", margin: "0 6px" },

  stageTitle: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 32, letterSpacing: "0.03em", marginBottom: 6, color: "#1a1a1a" },
  stageSub: { fontSize: 14, color: "#888", marginBottom: 28, fontWeight: 300 },
  errorBar: { background: "#fff5f5", border: "1px solid #fca5a5", borderRadius: 8, padding: "12px 16px", fontSize: 13, color: "#c00", marginBottom: 20 },

  dropzone: { border: "2px dashed #d0d0c8", borderRadius: 12, padding: "44px 24px", textAlign: "center", cursor: "pointer", transition: "all 0.2s", marginBottom: 24, background: "#fafaf8" },
  dropzoneHover: { borderColor: "#1a7f4b", background: "#f4fbf7" },
  loadingState: { display: "flex", flexDirection: "column", alignItems: "center", gap: 14 },
  loadingText: { fontSize: 14, color: "#666", fontWeight: 300 },
  spinner: { width: 36, height: 36, border: "3px solid #e0ede6", borderTop: "3px solid #1a7f4b", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
  spinnerWhite: { width: 14, height: 14, border: "2px solid rgba(255,255,255,0.4)", borderTop: "2px solid #fff", borderRadius: "50%", animation: "spin 0.8s linear infinite", display: "inline-block" },
  uploadIcon: { marginBottom: 14 },
  dropTitle: { fontSize: 16, fontWeight: 700, marginBottom: 6, color: "#1a1a1a" },
  dropSub: { fontSize: 13, color: "#aaa", marginBottom: 20, fontWeight: 300 },
  fileBtn: { display: "inline-block", background: "#1a7f4b", color: "#fff", borderRadius: 6, padding: "10px 24px", fontSize: 13, fontWeight: 700, cursor: "pointer" },

  formRow: { display: "flex", alignItems: "center", gap: 16, marginBottom: 20, flexWrap: "wrap" },
  formGroup: { marginBottom: 20 },
  formLabel: { fontSize: 13, fontWeight: 700, color: "#444", whiteSpace: "nowrap" },
  optionalTag: { fontWeight: 300, color: "#aaa", fontSize: 12, marginLeft: 6 },
  select: { border: "1px solid #d8d8d0", borderRadius: 8, padding: "9px 12px", fontSize: 13, background: "#fff", cursor: "pointer", color: "#333", fontFamily: "'Lato', sans-serif" },
  textarea: { width: "100%", border: "1px solid #d8d8d0", borderRadius: 8, padding: "12px", fontSize: 14, fontFamily: "'Lato', sans-serif", resize: "vertical", color: "#222", lineHeight: 1.6, fontWeight: 300, marginTop: 8 },
  fieldHint: { fontSize: 12, color: "#aaa", marginTop: 8, fontWeight: 300 },

  docTagsRow: { display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 },
  docTag: { background: "#f0f0ec", borderRadius: 20, padding: "4px 12px", fontSize: 11, color: "#777", fontWeight: 400 },

  uploadedBadge: { display: "flex", alignItems: "center", gap: 14, background: "#f4fbf7", border: "1px solid #b8e8cc", borderRadius: 10, padding: "14px 16px", marginBottom: 20 },
  uploadedIconBox: { width: 42, height: 42, background: "#1a7f4b", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15, fontWeight: 700, borderRadius: 8, flexShrink: 0 },
  uploadedInfo: { flex: 1 },
  uploadedType: { fontSize: 14, fontWeight: 700, textTransform: "capitalize", marginBottom: 3, color: "#1a1a1a" },
  uploadedMeta: { fontSize: 12, color: "#777", fontWeight: 300 },
  checkmark: { fontSize: 12, color: "#1a7f4b", fontWeight: 700 },

  previewBox: { background: "#f7f7f5", borderRadius: 8, padding: "14px 16px", marginBottom: 20, border: "1px solid #e8e8e4" },
  previewLabel: { fontSize: 11, fontWeight: 700, color: "#aaa", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 },
  previewText: { fontSize: 13, color: "#555", lineHeight: 1.6, fontWeight: 300 },

  btnPrimary: { background: "#1a7f4b", color: "#fff", border: "none", borderRadius: 8, padding: "13px 28px", fontSize: 14, fontWeight: 700, cursor: "pointer", width: "100%", letterSpacing: "0.01em" },
  btnGhost: { background: "#88c4a4", color: "#fff", border: "none", borderRadius: 8, padding: "13px 28px", fontSize: 14, fontWeight: 700, cursor: "not-allowed", width: "100%" },
  btnRow: { display: "flex", alignItems: "center", justifyContent: "center", gap: 10 },

  resultsTop: { display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28, paddingBottom: 20, borderBottom: "1px solid #f0f0ec", flexWrap: "wrap", gap: 12 },
  resultsDocRow: { display: "flex", alignItems: "center", gap: 14 },
  resultsIconBox: { width: 48, height: 48, background: "#1a1a1a", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700, borderRadius: 10, flexShrink: 0 },
  resultsDocName: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 24, letterSpacing: "0.03em", textTransform: "capitalize", marginBottom: 4 },
  resultsDocMeta: { fontSize: 12, color: "#888", fontWeight: 300 },
  newBtn: { background: "transparent", border: "1px solid #d8d8d0", borderRadius: 6, padding: "8px 16px", fontSize: 12, fontWeight: 700, cursor: "pointer", color: "#555", whiteSpace: "nowrap" },

  section: { marginBottom: 32, paddingBottom: 32, borderBottom: "1px solid #f0f0ec" },
  sectionLabel: { fontSize: 10, fontWeight: 700, letterSpacing: "0.18em", textTransform: "uppercase", color: "#aaa", marginBottom: 14 },
  sectionLabelRow: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 },
  explanation: { fontSize: 15, lineHeight: 1.8, color: "#333", fontWeight: 300 },

  stepsList: { display: "flex", flexDirection: "column", gap: 10 },
  stepCard: { borderLeft: "3px solid", borderRadius: "0 8px 8px 0", padding: "14px 16px" },
  stepHeader: { display: "flex", alignItems: "center", gap: 8, marginBottom: 10, flexWrap: "wrap" },
  stepNum: { color: "#fff", borderRadius: 4, padding: "2px 8px", fontSize: 10, fontWeight: 700, letterSpacing: "0.06em" },
  priorityBadge: { border: "1px solid", borderRadius: 4, padding: "2px 8px", fontSize: 10, fontWeight: 700, letterSpacing: "0.06em" },
  deadlineChip: { fontSize: 11, color: "#888", fontWeight: 300 },
  stepText: { fontSize: 14, color: "#333", lineHeight: 1.6, fontWeight: 300, marginBottom: 6 },
  stepLink: { fontSize: 12, color: "#1a7f4b", textDecoration: "none", fontWeight: 400 },

  deadlinesList: { display: "flex", flexDirection: "column", gap: 8 },
  deadlineCard: { display: "flex", gap: 16, padding: "12px 16px", background: "#fffbf0", border: "1px solid #ffe4a0", borderRadius: 8, alignItems: "flex-start" },
  deadlineDate: { fontSize: 12, fontWeight: 700, color: "#b06000", minWidth: 88, whiteSpace: "nowrap" },
  deadlineDesc: { fontSize: 13, color: "#555", lineHeight: 1.5, fontWeight: 300 },

  // Letter section — redesigned
  letterSection: { marginBottom: 32, borderRadius: 12, overflow: "hidden", border: "2px solid #1a7f4b", boxShadow: "0 4px 24px rgba(26,127,75,0.15)" },
  letterHeader: { background: "#1a7f4b", padding: "20px 24px" },
  letterTitleRow: { display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 12 },
  letterIcon: { fontSize: 28, flexShrink: 0, marginTop: 2 },
  letterTitle: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 28, letterSpacing: "0.06em", color: "#fff", marginBottom: 2 },
  letterSubtitle: { fontSize: 12, color: "rgba(255,255,255,0.75)", fontWeight: 300 },
  importantBadge: { marginLeft: "auto", background: "#fff", color: "#1a7f4b", fontSize: 10, fontWeight: 700, letterSpacing: "0.12em", padding: "4px 10px", borderRadius: 4, flexShrink: 0, alignSelf: "flex-start" },
  letterWarning: { background: "rgba(255,255,255,0.15)", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#fff", lineHeight: 1.5 },
  letterBody: { background: "#fafaf8", padding: "24px", fontSize: 13, lineHeight: 1.9, whiteSpace: "pre-wrap", fontFamily: "'Lato', sans-serif", color: "#333", overflowX: "auto", fontWeight: 300, margin: 0 },
  letterActions: { display: "flex", gap: 12, padding: "16px 24px", background: "#f0f8f4", borderTop: "1px solid #d0e8d8", flexWrap: "wrap" },
  letterCopyBtn: { background: "#fff", border: "1px solid #1a7f4b", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer", color: "#1a7f4b" },
  letterPdfBtn: { background: "#1a7f4b", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer", color: "#fff" },

  translateRow: { display: "flex", gap: 10, flexWrap: "wrap" },
  outlineBtn: { width: "100%", background: "transparent", border: "1.5px solid #d8d8d0", borderRadius: 8, padding: "13px", fontSize: 13, fontWeight: 700, cursor: "pointer", color: "#555", marginTop: 8 },

  footer: { background: "#fff", borderTop: "1px solid #e8e8e4", padding: "20px 24px" },
  footerInner: { maxWidth: 1120, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 },
  footerLeft: { display: "flex", alignItems: "center", gap: 10 },
  footerBrand: { fontFamily: "'Bebas Neue', sans-serif", fontSize: 18, letterSpacing: "0.04em", color: "#1a1a1a" },
  footerRight: { fontSize: 12, color: "#aaa", fontWeight: 300 },
};