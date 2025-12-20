import { motion } from 'framer-motion';

export function HeroCircuitBackground() {
  return (
    <svg
      className="absolute inset-0 w-full h-full"
      viewBox="0 0 1200 800"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Left circuit lines */}
      <g opacity="0.4">
        {/* Top left line */}
        <path
          d="M 100 200 L 400 200 L 500 250"
          stroke="url(#circuit-gradient)"
          strokeWidth="2"
          strokeDasharray="4 4"
        />
        {/* Bottom left line */}
        <path
          d="M 150 400 L 450 400 L 500 350"
          stroke="url(#circuit-gradient)"
          strokeWidth="2"
          strokeDasharray="4 4"
        />
      </g>

      {/* Right circuit lines */}
      <g opacity="0.4">
        {/* Top right line */}
        <path
          d="M 1100 200 L 800 200 L 700 250"
          stroke="url(#circuit-gradient)"
          strokeWidth="2"
          strokeDasharray="4 4"
        />
        {/* Bottom right line */}
        <path
          d="M 1050 400 L 750 400 L 700 350"
          stroke="url(#circuit-gradient)"
          strokeWidth="2"
          strokeDasharray="4 4"
        />
      </g>

      {/* Pulsing signals - animated circles */}
      <motion.circle
        cx="100"
        cy="200"
        r="4"
        fill="#10b981"
        initial={{ cx: 100, opacity: 0 }}
        animate={{
          cx: [100, 400, 500],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
          delay: 0,
        }}
      />
      <motion.circle
        cx="150"
        cy="400"
        r="4"
        fill="#10b981"
        initial={{ cx: 150, opacity: 0 }}
        animate={{
          cx: [150, 450, 500],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
          delay: 1,
        }}
      />
      <motion.circle
        cx="1100"
        cy="200"
        r="4"
        fill="#10b981"
        initial={{ cx: 1100, opacity: 0 }}
        animate={{
          cx: [1100, 800, 700],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
          delay: 0.5,
        }}
      />
      <motion.circle
        cx="1050"
        cy="400"
        r="4"
        fill="#10b981"
        initial={{ cx: 1050, opacity: 0 }}
        animate={{
          cx: [1050, 750, 700],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
          delay: 1.5,
        }}
      />

      {/* Gradient definitions */}
      <defs>
        <linearGradient id="circuit-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#374151" />
          <stop offset="50%" stopColor="#10b981" stopOpacity="0.5" />
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
        y: [0, -10, 0],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <div className="w-16 h-16 rounded-xl bg-slate-800/60 backdrop-blur-md border border-emerald-500/20 flex items-center justify-center">
        <Icon className="w-8 h-8 text-emerald-400/60" />
      </div>
    </motion.div>
  );
}
