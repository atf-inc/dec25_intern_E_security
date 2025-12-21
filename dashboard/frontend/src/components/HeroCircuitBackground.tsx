import { motion } from 'framer-motion';

export function HeroCircuitBackground() {
  return (
    <svg
      className="absolute inset-0 w-full h-full"
      viewBox="0 0 1200 600"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Compact circuit lines - bento grid style */}
      <g opacity="0.5">
        {/* Top left line */}
        <path
          d="M 350 180 L 520 180 L 560 220"
          stroke="url(#circuit-gradient)"
          strokeWidth="1.5"
          strokeDasharray="3 3"
        />
        {/* Bottom left line */}
        <path
          d="M 350 320 L 520 320 L 560 280"
          stroke="url(#circuit-gradient)"
          strokeWidth="1.5"
          strokeDasharray="3 3"
        />
        {/* Top right line */}
        <path
          d="M 850 180 L 680 180 L 640 220"
          stroke="url(#circuit-gradient)"
          strokeWidth="1.5"
          strokeDasharray="3 3"
        />
        {/* Bottom right line */}
        <path
          d="M 850 320 L 680 320 L 640 280"
          stroke="url(#circuit-gradient)"
          strokeWidth="1.5"
          strokeDasharray="3 3"
        />
      </g>

      {/* Pulsing signals - animated dots */}
      <motion.circle
        cx="350"
        cy="180"
        r="3"
        fill="#10b981"
        initial={{ cx: 350, opacity: 0 }}
        animate={{
          cx: [350, 520, 560],
          cy: [180, 180, 220],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0,
        }}
      />
      <motion.circle
        cx="350"
        cy="320"
        r="3"
        fill="#10b981"
        initial={{ cx: 350, opacity: 0 }}
        animate={{
          cx: [350, 520, 560],
          cy: [320, 320, 280],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.8,
        }}
      />
      <motion.circle
        cx="850"
        cy="180"
        r="3"
        fill="#10b981"
        initial={{ cx: 850, opacity: 0 }}
        animate={{
          cx: [850, 680, 640],
          cy: [180, 180, 220],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.4,
        }}
      />
      <motion.circle
        cx="850"
        cy="320"
        r="3"
        fill="#10b981"
        initial={{ cx: 850, opacity: 0 }}
        animate={{
          cx: [850, 680, 640],
          cy: [320, 320, 280],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1.2,
        }}
      />

      {/* Gradient definitions */}
      <defs>
        <linearGradient id="circuit-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#374151" />
          <stop offset="50%" stopColor="#10b981" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#374151" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function FloatingNode({ icon: Icon, position }: { icon: any; position: string }) {
  return (
    <motion.div
      className={`absolute ${position} hidden lg:block`}
      animate={{
        y: [0, -8, 0],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <div className="w-12 h-12 rounded-lg bg-slate-800/70 backdrop-blur-md border border-emerald-500/30 flex items-center justify-center shadow-lg">
        <Icon className="w-6 h-6 text-emerald-400/70" />
      </div>
    </motion.div>
  );
}
