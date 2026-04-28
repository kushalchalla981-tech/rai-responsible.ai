import { useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer, Cell
} from "recharts";
import api from "../api";

const THRESHOLD = 0.8;

function StatusCard({ result, delay }) {
  // Handle the case where result might be undefined or not have the expected structure
  if (!result || typeof result !== 'object') {
    return null;
  }
  
  const pass = result.status === "PASS";
  const value = result.value !== undefined ? result.value : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      style={cardStyle}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
        <div>
          <p style={metricLabelStyle}>{result.metric ? result.metric.replace(/_/g, " ") : "Metric"}</p>
          <p style={{ ...valueStyle, color: pass ? "#f2f0eb" : "#e05555" }}>
            {(value * 100).toFixed(1)}%
          </p>
        </div>
        <span style={{
          ...statusBadgeStyle,
          color: pass ? "#4ade80" : "#e05555",
          borderColor: pass ? "rgba(74,222,128,0.25)" : "rgba(224,85,85,0.25)",
        }}>
          {result.status || "N/A"}
        </span>
      </div>
      <div style={detailsStyle}>
        <span>Threshold: {((result.threshold || 0.8) * 100).toFixed(0)}%</span>
        <span>Risk: {result.risk || "N/A"}</span>
        {result.majority_group && <span>Ref: {result.majority_group}</span>}
        {result.minority_group && <span>Min: {result.minority_group}</span>}
      </div>
    </motion.div>
  );
}

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={tooltipStyle}>
      <div style={{ color: "#f2f0eb", marginBottom: 4 }}>{label}</div>
      <div>{(payload[0].value * 100).toFixed(1)}%</div>
    </div>
  );
};

function GroupChart({ groupRates, sensitiveCol }) {
  return (
    <div style={{ marginTop: 28, paddingTop: 24, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
      <p style={chartLabelStyle}>Positive rate by group</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={groupRates} layout="vertical" margin={{ left: 16, right: 32, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
          <XAxis
            type="number" domain={[0, 1]} tickFormatter={v => `${(v * 100).toFixed(0)}%`}
            tick={{ fill: "rgba(255,255,255,0.2)", fontSize: 11, fontFamily: "'DM Sans', sans-serif" }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
          />
          <YAxis
            type="category" dataKey={sensitiveCol}
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 12, fontFamily: "'DM Sans', sans-serif" }}
            axisLine={{ stroke: "rgba(255,255,255,0.06)" }}
            tickLine={false}
            width={90}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
          <ReferenceLine x={THRESHOLD} stroke="rgba(224,85,85,0.4)" strokeWidth={1} strokeDasharray="4 4" />
          <Bar dataKey="positive_rate" radius={[0, 2, 2, 0]} maxBarSize={28}>
            {groupRates.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.positive_rate >= THRESHOLD ? "rgba(255,255,255,0.35)" : "rgba(224,85,85,0.5)"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p style={thresholdHintStyle}>— 80% threshold (four-fifths rule)</p>
    </div>
  );
}

export default function MetricsPanel({ results }) {
  const [summaries, setSummaries] = useState({});
  const [loadingSummary, setLoadingSummary] = useState({});

  const generateSummary = async (col, data) => {
    setLoadingSummary(prev => ({ ...prev, [col]: true }));
    try {
      const { data: responseData } = await api.post("/api/v1/audit/gemini-summary", {
        session_id: results[col]?._sessionId || "",
        sensitive_col: col,
        target_col: data._targetCol || "",
        results: { [col]: data },
      });
      setSummaries(prev => ({ ...prev, [col]: responseData.summary }));
    } catch (e) {
      console.error("Failed to generate Gemini summary:", e);
      setSummaries(prev => ({ ...prev, [col]: "Failed to generate AI summary. Please try again." }));
    } finally {
      setLoadingSummary(prev => ({ ...prev, [col]: false }));
    }
  };

  if (!results) return null;

  return (
    <section style={sectionStyle}>
      <div style={containerStyle}>
        <motion.div
          style={{ marginBottom: 36 }}
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <p style={stepLabelStyle}>Step 03</p>
          <h2 style={headingStyle}>Fairness results</h2>
        </motion.div>

        <div style={{ display: "flex", flexDirection: "column", gap: 48 }}>
          {Object.entries(results).map(([col, data], colIdx) => (
            <motion.div
              key={col}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: colIdx * 0.08, duration: 0.6 }}
              style={resultBlockStyle}
            >
              <h3 style={colHeadingStyle}>{col}</h3>

            <div style={cardsGridStyle}>
              <StatusCard result={data.demographic_parity_ratio} delay={colIdx * 0.08} />
              <StatusCard result={data.demographic_parity_difference} delay={colIdx * 0.08 + 0.08} />
            </div>

            {data.group_rates && data.group_rates.length > 0 && (
              <GroupChart groupRates={data.group_rates} sensitiveCol={col} />
            )}

            {/* Gemini AI Summary Section */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: colIdx * 0.08 + 0.2 }}
              style={geminiSectionStyle}
            >
              {!summaries[col] && !loadingSummary[col] && (
                <button
                  onClick={() => generateSummary(col, data)}
                  style={geminiButtonStyle}
                  onMouseEnter={(e) => { e.target.style.background = "rgba(0,229,255,0.15)"; e.target.style.borderColor = "rgba(0,229,255,0.4)"; }}
                  onMouseLeave={(e) => { e.target.style.background = "rgba(0,229,255,0.08)"; e.target.style.borderColor = "rgba(0,229,255,0.2)"; }}
                >
                  ✦ Generate AI Summary with Gemini
                </button>
              )}

              {loadingSummary[col] && (
                <div style={geminiLoadingStyle}>
                  <div style={geminiSpinnerStyle} />
                  <span style={geminiLoadingTextStyle}>Generating AI summary...</span>
                </div>
              )}

              {summaries[col] && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={geminiSummaryStyle}
                >
                  <p style={geminiSummaryLabelStyle}>✦ AI-Powered Summary (Gemini)</p>
                  <p style={geminiSummaryTextStyle}>{summaries[col]}</p>
                </motion.div>
              )}
            </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── Styles ──

const sectionStyle = {
  padding: "0",
  background: "transparent",
};

const containerStyle = {
  width: "100%",
};

const stepLabelStyle = {
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  fontSize: 13,
  fontWeight: 600,
  color: "rgba(255,255,255,0.45)",
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  margin: 0,
};

const headingStyle = {
  fontFamily: "'Sora', sans-serif",
  fontSize: "clamp(28px, 4vw, 38px)",
  fontWeight: 400,
  letterSpacing: "-0.02em",
  color: "#f2f0eb",
  lineHeight: 1.15,
  margin: "8px 0 0",
};

const resultBlockStyle = {
  border: "1px solid rgba(255,255,255,0.08)",
  borderTop: "1px solid rgba(255,255,255,0.15)",
  borderLeft: "1px solid rgba(255,255,255,0.12)",
  padding: 32,
  background: "linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)",
  backdropFilter: "blur(12px) saturate(120%)",
  WebkitBackdropFilter: "blur(12px) saturate(120%)",
  borderRadius: 24,
  boxShadow: "0 16px 40px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.08)",
};

const colHeadingStyle = {
  fontFamily: "'Sora', sans-serif",
  fontSize: 22,
  fontWeight: 400,
  color: "#f2f0eb",
  letterSpacing: "-0.02em",
  marginBottom: 24,
  paddingBottom: 16,
  borderBottom: "1px solid rgba(255,255,255,0.1)",
  textTransform: "capitalize",
};

const cardStyle = {
  border: "1px solid rgba(255,255,255,0.08)",
  borderTop: "1px solid rgba(255,255,255,0.15)",
  padding: 24,
  background: "rgba(255,255,255,0.03)",
  backdropFilter: "blur(8px) saturate(130%)",
  WebkitBackdropFilter: "blur(8px) saturate(130%)",
  borderRadius: 16,
};

const cardsGridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: 16,
};

const metricLabelStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 14,
  fontWeight: 500,
  color: "rgba(255,255,255,0.6)",
  marginBottom: 8,
  textTransform: "capitalize",
};

const valueStyle = {
  fontFamily: "'Sora', sans-serif",
  fontSize: 36,
  fontWeight: 400,
  margin: 0,
  lineHeight: 1,
};

const statusBadgeStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 12,
  fontWeight: 600,
  letterSpacing: "0.06em",
  border: "1px solid",
  padding: "4px 12px",
  borderRadius: 8,
};

const detailsStyle = {
  display: "flex",
  flexWrap: "wrap",
  gap: "8px 16px",
  fontFamily: "'Inter', sans-serif",
  fontSize: 12,
  fontWeight: 500,
  color: "rgba(255,255,255,0.45)",
};

const tooltipStyle = {
  background: "linear-gradient(135deg, rgba(30,30,35,0.8) 0%, rgba(15,15,20,0.8) 100%)",
  backdropFilter: "blur(16px)",
  border: "1px solid rgba(255,255,255,0.15)",
  padding: "10px 14px",
  fontFamily: "'Inter', sans-serif",
  fontSize: 13,
  fontWeight: 500,
  color: "rgba(255,255,255,0.8)",
  boxShadow: "0 10px 20px rgba(0,0,0,0.4)",
  borderRadius: 8,
};

const chartLabelStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 13,
  fontWeight: 600,
  color: "rgba(255,255,255,0.7)",
  marginBottom: 20,
};

const thresholdHintStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 12,
  fontWeight: 500,
  color: "rgba(224,85,85,0.7)",
  marginTop: 12,
};

const geminiSectionStyle = {
  marginTop: 28,
  paddingTop: 24,
  borderTop: "1px solid rgba(0,229,255,0.1)",
};

const geminiButtonStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 13,
  fontWeight: 600,
  color: "rgba(0,229,255,0.8)",
  background: "rgba(0,229,255,0.08)",
  border: "1px solid rgba(0,229,255,0.2)",
  padding: "12px 24px",
  borderRadius: 12,
  cursor: "pointer",
  transition: "all 0.2s ease",
  letterSpacing: "0.02em",
};

const geminiLoadingStyle = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  padding: "16px 0",
};

const geminiSpinnerStyle = {
  width: 20,
  height: 20,
  border: "2px solid rgba(0,229,255,0.2)",
  borderTop: "2px solid rgba(0,229,255,0.8)",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
};

const geminiLoadingTextStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 13,
  color: "rgba(255,255,255,0.5)",
};

const geminiSummaryStyle = {
  background: "rgba(0,229,255,0.04)",
  border: "1px solid rgba(0,229,255,0.12)",
  borderRadius: 16,
  padding: 24,
  marginTop: 16,
};

const geminiSummaryLabelStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 12,
  fontWeight: 600,
  color: "rgba(0,229,255,0.6)",
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  marginBottom: 12,
};

const geminiSummaryTextStyle = {
  fontFamily: "'Inter', sans-serif",
  fontSize: 14,
  fontWeight: 400,
  color: "rgba(255,255,255,0.75)",
  lineHeight: 1.7,
  margin: 0,
  whiteSpace: "pre-wrap",
};
