import { motion } from 'framer-motion';
import { type ReactNode } from 'react';

interface FloatingCardProps {
  children: ReactNode;
  delay?: number;
  duration?: number;
}

export function FloatingCard({ children, delay = 0, duration = 3 }: FloatingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{
        opacity: [0.7, 1, 0.7],
        y: [0, -20, 0],
        scale: [0.95, 1, 0.95],
      }}
      transition={{
        duration,
        delay,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      className="glass-card p-4 text-sm"
    >
      {children}
    </motion.div>
  );
}
