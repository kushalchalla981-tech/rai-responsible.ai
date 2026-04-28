// src/components/HeroScene/index.jsx
import { useRef, useEffect, useState, useCallback } from "react";
import { useScroll, useTransform, motion, useReducedMotion, AnimatePresence } from "framer-motion";
import Figure from "./Figure";
import { FIGURES } from "./figures";

// Inject marquee + orb + scan-line keyframes into the document once
const KEYFRAMES_ID = "fairplay-marquee-keyframes";
function injectKeyframes() {
  if (document.getElementById(KEYFRAMES_ID)) return;
  const style = document.createElement("style");
  style.id = KEYFRAMES_ID;
  style.textContent = `
    @keyframes marqueeL2R {
      0% { transform: translateX(-15vw); }
      100% { transform: translateX(110vw); }
    }
    @keyframes marqueeR2L {
      0% { transform: translateX(110vw); }
      100% { transform: translateX(-15vw); }
    }
    @keyframes figDrift {
      0% { transform: translateY(0); }
      100% { transform: translateY(-6px); }
    }
    @keyframes orbFloat1 {
      0%, 100% { transform: translate(0, 0) scale(1); }
      25% { transform: translate(30px, -40px) scale(1.05); }
      50% { transform: translate(-20px, -80px) scale(0.95); }
      75% { transform: translate(40px, -30px) scale(1.02); }
    }
    @keyframes orbFloat2 {
      0%, 100% { transform: translate(0, 0) scale(1); }
      33% { transform: translate(-40px, 30px) scale(1.08); }
      66% { transform: translate(25px, 50px) scale(0.92); }
    }
    @keyframes orbFloat3 {
      0%, 100% { transform: translate(0, 0) scale(1); }
      50% { transform: translate(35px, -25px) scale(1.06); }
    }
    @keyframes scanLine {
      0% { transform: translateY(-10%); opacity: 0; }
      10% { opacity: 0.04; }
      90% { opacity: 0.04; }
      100% { transform: translateY(110vh); opacity: 0; }
    }
    @keyframes titleGlow {
      0%, 100% { text-shadow: 0 0 20px rgba(0,229,255,0.2), 0 0 60px rgba(0,229,255,0.08); }
      50% { text-shadow: 0 0 30px rgba(0,229,255,0.35), 0 0 80px rgba(0,229,255,0.12); }
    }
    @keyframes glitchFlicker {
      0%, 100% { clip-path: inset(0 0 0 0); transform: translateX(0); }
      92% { clip-path: inset(0 0 0 0); transform: translateX(0); }
      93% { clip-path: inset(30% 0 40% 0); transform: translateX(2px); }
      94% { clip-path: inset(0 0 0 0); transform: translateX(0); }
      95% { clip-path: inset(50% 0 20% 0); transform: translateX(-1px); }
      96% { clip-path: inset(0 0 0 0); transform: translateX(0); }
    }
    @keyframes statsCount {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `;
  document.head.appendChild(style);
}

// Mouse parallax hook
function useMouseParallax(ref) {
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const onMove = useCallback((e) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    setOffset({
      x: ((e.clientX - rect.left) / rect.width - 0.5) * 12,
      y: ((e.clientY - rect.top) / rect.height - 0.5) * 8,
    });
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, [onMove]);

  return offset;
}

// Domain pills data
const DOMAIN_PILLS = [
  { label: "Healthcare", color: "rgba(52,211,153,0.3)" },
  { label: "Hiring", color: "rgba(96,165,250,0.3)" },
  { label: "Lending", color: "rgba(251,191,36,0.3)" },
  { label: "Insurance", color: "rgba(251,146,60,0.3)" },
];

// Cycling subtitles
const SUBTITLES = [
  "Detect. Measure. Correct — AI Bias Ends Here.",
  "Healthcare. Hiring. Lending. Insurance.",
];

export default function HeroScene() {
  const sectionRef = useRef(null);
  const crowdRef = useRef(null);
  const shouldReduce = useReducedMotion();
  const mouseOffset = useMouseParallax(sectionRef);

  const [subtitleIndex, setSubtitleIndex] = useState(0);
  useEffect(() => {
    if (shouldReduce) return;
    const interval = setInterval(() => {
      setSubtitleIndex((i) => (i + 1) % SUBTITLES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [shouldReduce]);

  // Stats counter animation
  const [statsVisible, setStatsVisible] = useState(false);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end start"],
  });

  useEffect(() => {
    const unsubscribe = scrollYProgress.on("change", (v) => {
      if (v > 0.08 && v < 0.35) {
        setStatsVisible(true);
      }
    });
    return unsubscribe;
  }, [scrollYProgress]);

  useEffect(() => {
    injectKeyframes();
  }, []);

  // Title animations
  const titleOpacity = useTransform(scrollYProgress, [0, 0.25, 0.5], [1, 0.9, 0]);
  const titleY = useTransform(scrollYProgress, [0, 0.5], ["0%", "-12%"]);
  const titleScale = useTransform(scrollYProgress, [0, 0.5], [1, 0.92]);

  // Subtitle
  const subOpacity = useTransform(scrollYProgress, [0, 0.15, 0.4], [1, 0.8, 0]);

  // Vignette
  const vignetteOpacity = useTransform(scrollYProgress, [0, 0.4], [0.6, 0]);

  if (shouldReduce) {
    return (
      <section
        style={{
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#080808",
          flexDirection: "column",
          gap: "16px",
        }}
      >
        <h1 style={titleStyle}>RAI</h1>
        <p style={subtitleStyle}>
          Detect. Measure. Correct — AI Bias Ends Here.
        </p>
      </section>
    );
  }

  return (
    <section
      ref={sectionRef}
      style={{
        position: "relative",
        height: "200vh",
      }}
    >
      {/* Sticky viewport */}
      <div
        style={{
          position: "sticky",
          top: 0,
          height: "100vh",
          overflow: "hidden",
          background: "#080808",
        }}
      >
        {/* Floating gradient orbs */}
        <div style={orb1Style} />
        <div style={orb2Style} />
        <div style={orb3Style} />

        {/* Scan line */}
        <div style={scanLineStyle} />

        {/* Subtle dot grid */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "radial-gradient(rgba(255,255,255,0.018) 1px, transparent 1px)",
            backgroundSize: "32px 32px",
            pointerEvents: "none",
            zIndex: 0,
          }}
        />

        {/* TITLE BLOCK (centered) */}
        <motion.div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            paddingBottom: "30vh",
            zIndex: 20,
            pointerEvents: "none",
            opacity: titleOpacity,
            y: titleY,
            scale: titleScale,
          }}
        >
          {/* Glitch layer behind title */}
          <motion.div
            style={{
              position: "absolute",
              animation: "glitchFlicker 8s infinite",
              pointerEvents: "none",
              zIndex: -1,
            }}
          >
            <motion.h1
              style={{
                ...titleStyle,
                color: "rgba(0,229,255,0.15)",
                animation: "none",
              }}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            >
              RAI
            </motion.h1>
          </motion.div>

          <motion.h1
            style={{
              ...titleStyle,
              animation: "titleGlow 4s ease-in-out infinite",
            }}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          >
            RAI
          </motion.h1>

          {/* Curved underline swoosh */}
          <motion.svg
            viewBox="0 0 320 20"
            fill="none"
            style={{
              width: "clamp(200px, 35vw, 420px)",
              height: "auto",
              marginTop: -4,
              overflow: "visible",
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <motion.path
              d="M10 14 Q80 -4 160 10 Q240 24 310 6"
              stroke="rgba(255,255,255,0.25)"
              strokeWidth="2"
              strokeLinecap="round"
              fill="none"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.2, delay: 0.8, ease: [0.22, 1, 0.36, 1] }}
            />
          </motion.svg>

          {/* Domain pills */}
          <motion.div
            style={pillsContainerStyle}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 1.0, ease: [0.22, 1, 0.36, 1] }}
          >
            {DOMAIN_PILLS.map((pill, i) => (
              <motion.span
                key={pill.label}
                style={{
                  ...pillStyle,
                  borderColor: pill.color,
                  background: pill.color,
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 1.0 + i * 0.12 }}
              >
                {pill.label}
              </motion.span>
            ))}
          </motion.div>

          {/* Cycling subtitle */}
          <div style={{ height: 28, marginTop: 12 }}>
            <AnimatePresence mode="wait">
              <motion.p
                key={subtitleIndex}
                style={subtitleStyle}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.5 }}
              >
                {SUBTITLES[subtitleIndex]}
              </motion.p>
            </AnimatePresence>
          </div>

          {/* Stats counter */}
          <motion.div
            style={{
              ...statsContainerStyle,
              opacity: statsVisible ? 1 : 0,
              y: statsVisible ? 0 : 10,
              transition: "opacity 0.6s, transform 0.6s",
            }}
          >
            <div style={statItemStyle}>
              <span style={statValueStyle}>4</span>
              <span style={statLabelStyle}>Domains</span>
            </div>
            <div style={statDividerStyle} />
            <div style={statItemStyle}>
              <span style={statValueStyle}>2500</span>
              <span style={statLabelStyle}>Records Each</span>
            </div>
            <div style={statDividerStyle} />
            <div style={statItemStyle}>
              <span style={statValueStyle}>80%</span>
              <span style={statLabelStyle}>Fairness Threshold</span>
            </div>
          </motion.div>
        </motion.div>

        {/* CROWD OF FIGURES — all 14 in 4 speed-layers */}
        <motion.div
          ref={crowdRef}
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "60%",
            zIndex: 15,
            pointerEvents: "none",
            x: mouseOffset.x,
            y: mouseOffset.y,
          }}
        >
          {FIGURES.map((fig, i) => (
            <Figure
              key={fig.id}
              data={fig}
              scrollProgress={scrollYProgress}
              index={i}
            />
          ))}
        </motion.div>

        {/* EDGE VIGNETTE */}
        <motion.div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(90deg, rgba(8,8,8,0.95) 0%, transparent 12%, transparent 88%, rgba(8,8,8,0.95) 100%)",
            pointerEvents: "none",
            zIndex: 16,
            opacity: vignetteOpacity,
          }}
        />

        {/* Bottom gradient fade */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "30%",
            background:
              "linear-gradient(to top, #080808 0%, transparent 100%)",
            pointerEvents: "none",
            zIndex: 17,
            opacity: 0.4,
          }}
        />
      </div>
    </section>
  );
}

// ── Shared styles ──
const titleStyle = {
  fontFamily: "'Bricolage Grotesque', 'Space Grotesk', sans-serif",
  fontSize: "clamp(56px, 11vw, 148px)",
  fontWeight: 300,
  letterSpacing: "-0.04em",
  color: "#f2f0eb",
  lineHeight: 1,
  margin: 0,
  textAlign: "center",
  textShadow: "0 4px 60px rgba(0,0,0,0.6)",
};

const subtitleStyle = {
  fontFamily: "'DM Sans', 'Space Grotesk', sans-serif",
  fontSize: "clamp(14px, 2vw, 20px)",
  fontWeight: 300,
  color: "rgba(255,255,255,0.38)",
  letterSpacing: "0.02em",
  margin: 0,
  textAlign: "center",
};

const pillsContainerStyle = {
  display: "flex",
  gap: 10,
  marginTop: 20,
  flexWrap: "wrap",
  justifyContent: "center",
};

const pillStyle = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 12,
  fontWeight: 500,
  color: "rgba(255,255,255,0.7)",
  border: "1px solid",
  borderRadius: 999,
  padding: "5px 14px",
  letterSpacing: "0.01em",
  backdropFilter: "blur(4px)",
};

const statsContainerStyle = {
  display: "flex",
  gap: 24,
  marginTop: 28,
  alignItems: "center",
  justifyContent: "center",
  fontFamily: "'Inter', sans-serif",
};

const statItemStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 4,
};

const statValueStyle = {
  fontSize: 18,
  fontWeight: 600,
  color: "rgba(255,255,255,0.6)",
  letterSpacing: "0.02em",
};

const statLabelStyle = {
  fontSize: 10,
  fontWeight: 500,
  color: "rgba(255,255,255,0.3)",
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};

const statDividerStyle = {
  width: 1,
  height: 32,
  background: "rgba(255,255,255,0.1)",
};

const orb1Style = {
  position: "absolute",
  top: "15%",
  left: "10%",
  width: 400,
  height: 400,
  borderRadius: "50%",
  background: "radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%)",
  animation: "orbFloat1 18s ease-in-out infinite",
  pointerEvents: "none",
  zIndex: 1,
};

const orb2Style = {
  position: "absolute",
  top: "25%",
  right: "15%",
  width: 350,
  height: 350,
  borderRadius: "50%",
  background: "radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%)",
  animation: "orbFloat2 22s ease-in-out infinite",
  pointerEvents: "none",
  zIndex: 1,
};

const orb3Style = {
  position: "absolute",
  bottom: "30%",
  left: "40%",
  width: 300,
  height: 300,
  borderRadius: "50%",
  background: "radial-gradient(circle, rgba(0,229,255,0.04) 0%, transparent 70%)",
  animation: "orbFloat3 20s ease-in-out infinite",
  pointerEvents: "none",
  zIndex: 1,
};

const scanLineStyle = {
  position: "absolute",
  top: 0,
  left: 0,
  right: 0,
  height: 2,
  background: "linear-gradient(90deg, transparent 0%, rgba(0,229,255,0.3) 50%, transparent 100%)",
  animation: "scanLine 6s linear infinite",
  pointerEvents: "none",
  zIndex: 2,
};
