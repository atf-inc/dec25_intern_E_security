import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Shield, Bot, Lock, Zap, Database, Bell, ArrowRight, Github, FileText, Users, Server, HardDrive, ExternalLink, Cloud, Activity, Code, Upload, AlertTriangle } from 'lucide-react';
import { GlassCard } from './GlassCard';
import { SimulationConsole } from './SimulationConsole';
import { HeroCircuitBackground, FloatingNode } from './HeroCircuitBackground';

export function LandingPage() {
  const navigate = useNavigate();

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-x-hidden">
      {/* Navigation Header */}
      <nav className="absolute top-0 w-full z-50">
        <div className="flex justify-between items-center px-6 py-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <Shield className="w-8 h-8 text-emerald-400" />
            <span className="text-xl font-bold tracking-tight">ShadowGuard</span>
          </div>
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-medium hover:bg-emerald-500/20 hover:border-emerald-500/30 transition-all backdrop-blur-sm"
          >
            Login
          </button>
        </div>
      </nav>

      {/* Hero Section - EqtyLab Style */}
      <section className="relative min-h-screen flex items-center justify-center px-6 overflow-hidden">
        {/* Dark gradient background */}
        <div className="absolute inset-0 bg-gradient-to-b from-black via-slate-950 to-black"></div>

        {/* Circuit lines background */}
        <div className="absolute inset-0">
          <HeroCircuitBackground />
        </div>

        {/* Floating nodes at circuit endpoints - bento grid layout */}
        <FloatingNode icon={Database} position="top-[28%] left-[28%]" />
        <FloatingNode icon={Lock} position="top-[52%] left-[28%]" />
        <FloatingNode icon={Server} position="top-[28%] right-[28%]" />
        <FloatingNode icon={HardDrive} position="top-[52%] right-[28%]" />

        {/* Central content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          {/* Central glowing chip - smaller */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="mb-8"
          >
            <div className="inline-block relative">
              {/* Glow effect */}
              <div className="absolute inset-0 bg-emerald-500/30 blur-3xl rounded-3xl"></div>

              {/* Chip container - reduced size */}
              <div className="relative w-24 h-24 mx-auto rounded-xl bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border-2 border-emerald-500/40 flex items-center justify-center shadow-2xl">
                {/* Inner glow */}
                <div className="absolute inset-2 bg-emerald-500/10 rounded-lg"></div>

                {/* Logo/Icon - smaller */}
                <Shield className="w-12 h-12 text-emerald-400 relative z-10" strokeWidth={1.5} />

                {/* Corner accents */}
                <div className="absolute top-1.5 left-1.5 w-2.5 h-2.5 border-t-2 border-l-2 border-emerald-500/60"></div>
                <div className="absolute top-1.5 right-1.5 w-2.5 h-2.5 border-t-2 border-r-2 border-emerald-500/60"></div>
                <div className="absolute bottom-1.5 left-1.5 w-2.5 h-2.5 border-b-2 border-l-2 border-emerald-500/60"></div>
                <div className="absolute bottom-1.5 right-1.5 w-2.5 h-2.5 border-b-2 border-r-2 border-emerald-500/60"></div>

                {/* Pulsing ring */}
                <motion.div
                  className="absolute inset-0 rounded-xl border-2 border-emerald-500/40"
                  animate={{
                    scale: [1, 1.15, 1],
                    opacity: [0.4, 0, 0.4],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                ></motion.div>
              </div>
            </div>
          </motion.div>

          {/* Typography */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight tracking-tight">
              Detect Shadow IT
            </h1>

            <p className="text-lg md:text-xl text-gray-400 mb-10 mt-15 max-w-2xl mx-auto leading-relaxed">
              Real-time detection of unauthorized SaaS usage, Shadow AI, and file sharing in your corporate network.
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <button
                onClick={() => scrollToSection('simulation')}
                className="btn-primary group"
              >
                <span>Launch Simulation</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/dashboard')}
                className="btn-ghost group"
              >
                <ExternalLink className="w-5 h-5" />
                <span>View Dashboard</span>
              </button>
            </div>
          </motion.div>
        </div>

        {/* Curved horizon at bottom */}
        <div className="absolute bottom-0 left-0 right-0 h-32 overflow-hidden">
          <svg
            className="absolute bottom-0 w-full"
            viewBox="0 0 1200 120"
            preserveAspectRatio="none"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M 0 60 Q 300 20, 600 40 T 1200 60 L 1200 120 L 0 120 Z"
              fill="url(#horizon-gradient)"
              opacity="0.3"
            />
            <path
              d="M 0 70 Q 300 30, 600 50 T 1200 70"
              stroke="url(#horizon-stroke)"
              strokeWidth="2"
              fill="none"
            />
            <defs>
              <linearGradient id="horizon-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="horizon-stroke" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                <stop offset="50%" stopColor="#10b981" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.3" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-emerald-500/30 rounded-full flex items-start justify-center p-2">
            <div className="w-1 h-2 bg-emerald-400 rounded-full"></div>
          </div>
        </motion.div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="px-4 py-2 rounded-full border border-red-500/30 bg-red-500/10 text-red-400 text-sm font-medium">
              The Problem
            </span>
            <h2 className="text-4xl md:text-5xl font-bold mt-6 mb-4">
              New AI workflows equal <span className="text-emerald-400">New Threats</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-3xl mx-auto">
              Compromising AI Supply Chains. Employees unknowingly expose sensitive data through unapproved AI tools and shadow SaaS applications.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Bento Grid Visual */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="grid grid-cols-3 grid-rows-3 gap-3 aspect-square">
                {/* Main Card - Data Log Analysis (spans 2 cols, 2 rows) */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1, duration: 0.5 }}
                  className="col-span-2 row-span-2 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-emerald-500/20 p-6 relative overflow-hidden group"
                >
                  {/* Circuit pattern background */}
                  <div className="absolute inset-0 opacity-20">
                    <svg className="w-full h-full" viewBox="0 0 200 200">
                      <path d="M20 100 L60 100 L70 80 L90 80 L100 100 L180 100" stroke="#10b981" strokeWidth="1" fill="none" opacity="0.5" />
                      <path d="M100 20 L100 60 L80 70 L80 90 L100 100 L100 180" stroke="#10b981" strokeWidth="1" fill="none" opacity="0.5" />
                      <circle cx="60" cy="100" r="3" fill="#10b981" opacity="0.6" />
                      <circle cx="100" cy="60" r="3" fill="#10b981" opacity="0.6" />
                      <circle cx="140" cy="100" r="3" fill="#10b981" opacity="0.6" />
                      <circle cx="100" cy="140" r="3" fill="#10b981" opacity="0.6" />
                    </svg>
                  </div>

                  {/* Central glow */}
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-emerald-500/20 via-transparent to-transparent"></div>

                  {/* Content */}
                  <div className="relative z-10 h-full flex flex-col">
                    <h3 className="text-emerald-400 font-bold text-lg mb-auto">Data Log Analysis</h3>

                    {/* Floating document icons */}
                    <div className="flex-1 flex items-center justify-center relative">
                      <motion.div
                        animate={{ y: [-5, 5, -5] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute top-4 left-8"
                      >
                        <FileText className="w-8 h-8 text-emerald-500/60" />
                      </motion.div>
                      <motion.div
                        animate={{ y: [5, -5, 5] }}
                        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute top-8 right-12"
                      >
                        <Code className="w-6 h-6 text-emerald-500/50" />
                      </motion.div>
                      <motion.div
                        animate={{ y: [-3, 7, -3] }}
                        transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute bottom-16 left-16"
                      >
                        <Upload className="w-7 h-7 text-emerald-500/40" />
                      </motion.div>

                      {/* Central shield with glow */}
                      <motion.div
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="relative"
                      >
                        <div className="absolute inset-0 bg-emerald-500/30 blur-2xl rounded-full scale-150"></div>
                        <div className="relative bg-slate-800/80 p-4 rounded-xl border border-emerald-500/30">
                          <Shield className="w-12 h-12 text-emerald-400" />
                        </div>
                      </motion.div>
                    </div>

                    {/* Progress indicator */}
                    <div className="mt-auto">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Logs Processed:</span>
                        <span className="text-emerald-400 font-mono">99%</span>
                      </div>
                      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: "0%" }}
                          whileInView={{ width: "99%" }}
                          viewport={{ once: true }}
                          transition={{ duration: 1.5, delay: 0.5, ease: "easeOut" }}
                          className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-2">Real-time data stream active</p>
                    </div>
                  </div>
                </motion.div>

                {/* Top Right - Threats Detected */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                  className="rounded-2xl bg-gradient-to-br from-red-500/10 to-slate-950 border border-red-500/20 p-4 flex flex-col justify-between"
                >
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                  <div>
                    <motion.p
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="text-2xl font-bold text-white"
                    >
                      24
                    </motion.p>
                    <p className="text-xs text-gray-400">Threats</p>
                  </div>
                </motion.div>

                {/* Middle Right - AI Scans */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="rounded-2xl bg-gradient-to-br from-emerald-500/10 to-slate-950 border border-emerald-500/20 p-4 flex flex-col justify-between"
                >
                  <Bot className="w-6 h-6 text-emerald-400" />
                  <div>
                    <p className="text-2xl font-bold text-white">1.2k</p>
                    <p className="text-xs text-gray-400">AI Scans</p>
                  </div>
                </motion.div>

                {/* Right Column Bottom - Users Monitored */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.35, duration: 0.5 }}
                  className="rounded-2xl bg-gradient-to-br from-cyan-500/10 to-slate-950 border border-cyan-500/20 p-4 flex flex-col justify-between"
                >
                  <Users className="w-6 h-6 text-cyan-400" />
                  <div>
                    <p className="text-2xl font-bold text-white">156</p>
                    <p className="text-xs text-gray-400">Users</p>
                  </div>
                </motion.div>

                {/* Bottom Left - Cloud Activity */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="rounded-2xl bg-gradient-to-br from-blue-500/10 to-slate-950 border border-blue-500/20 p-4 flex flex-col justify-between"
                >
                  <Cloud className="w-6 h-6 text-blue-400" />
                  <div>
                    <p className="text-2xl font-bold text-white">47</p>
                    <p className="text-xs text-gray-400">SaaS Apps</p>
                  </div>
                </motion.div>

                {/* Bottom Right - Live Status */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                  className="rounded-2xl bg-gradient-to-br from-purple-500/10 to-slate-950 border border-purple-500/20 p-4 flex flex-col justify-between"
                >
                  <Activity className="w-6 h-6 text-purple-400" />
                  <div className="flex items-center gap-1.5">
                    <motion.div
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="w-2 h-2 bg-emerald-400 rounded-full"
                    />
                    <p className="text-xs text-gray-400">Live</p>
                  </div>
                </motion.div>
              </div>
            </motion.div>

            {/* Threat List */}
            <div className="space-y-4">
              <GlassCard delay={0.1}>
                <div className="p-8">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <span className="text-red-400">›</span> Unchecked Shadow AI Usage
                  </h3>
                  <p className="text-gray-400">Employees pasting sensitive code and PII into unapproved public LLMs.</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.2}>
                <div className="p-8">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <span className="text-red-400">›</span> Unauthorized Data Exfiltration
                  </h3>
                  <p className="text-gray-400">Silent uploads of corporate IP to file-sharing services like Mega.</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.3}>
                <div className="p-8">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <span className="text-red-400">›</span> Bypassing Legacy Firewalls
                  </h3>
                  <p className="text-gray-400">Encrypted SaaS traffic often evades traditional inspection tools.</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.4}>
                <div className="p-8">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <span className="text-red-400">›</span> Lack of Semantic Visibility
                  </h3>
                  <p className="text-gray-400">Security teams lack context on why a user accessed a site.</p>
                </div>
              </GlassCard>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-20 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Complete Visibility into <span className="text-emerald-400">Shadow AI</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-3xl mx-auto">
              Detect, Analyze, and Block unauthorized GenAI usage before data leaves your network.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard delay={0.1}>
              <div className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <Database className="w-8 h-8 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold mb-3">Real-Time Interception</h3>
                <p className="text-gray-400 mb-4">Collector Engine ingests logs instantly from any source (Zscaler, Firewalls)</p>
                <div className="text-sm text-emerald-400 font-mono">What data goes into an AI workflow</div>
              </div>
            </GlassCard>

            <GlassCard delay={0.2}>
              <div className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <Zap className="w-8 h-8 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold mb-3">AI-Powered Analysis</h3>
                <p className="text-gray-400 mb-4">OpenRouter LLM semantic analysis understands context, not just keywords</p>
                <div className="text-sm text-emerald-400 font-mono">What code is run and where it is executed</div>
              </div>
            </GlassCard>

            <GlassCard delay={0.3}>
              <div className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                  <Bell className="w-8 h-8 text-emerald-400" />
                </div>
                <h3 className="text-xl font-bold mb-3">Instant Response</h3>
                <p className="text-gray-400 mb-4">Automated Slack alerts and Dashboard visualizations in milliseconds</p>
                <div className="text-sm text-emerald-400 font-mono">The output is genuine and secure</div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Simulation Console Section */}
      <section id="simulation" className="py-20 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Test the <span className="text-emerald-400">Defense Grid</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Run live simulations against our AI engine right now.
            </p>
          </div>

          <SimulationConsole />
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              System <span className="text-emerald-400">Architecture</span>
            </h2>
          </div>

          <GlassCard>
            <div className="p-8">
              <div className="flex flex-wrap items-center justify-center gap-4 text-center">
                <div className="flex-1 min-w-[120px]">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <FileText className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-sm font-semibold">Logs</div>
                </div>

                <ArrowRight className="w-6 h-6 text-emerald-400" />

                <div className="flex-1 min-w-[120px]">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <Database className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-sm font-semibold">Collector</div>
                </div>

                <ArrowRight className="w-6 h-6 text-emerald-400" />

                <div className="flex-1 min-w-[120px]">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <Zap className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-sm font-semibold">Redis</div>
                </div>

                <ArrowRight className="w-6 h-6 text-emerald-400" />

                <div className="flex-1 min-w-[120px]">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <Bot className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-sm font-semibold">Worker</div>
                </div>

                <ArrowRight className="w-6 h-6 text-emerald-400" />

                <div className="flex-1 min-w-[120px]">
                  <div className="w-16 h-16 mx-auto mb-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <Shield className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-sm font-semibold">Dashboard</div>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-gray-800">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-emerald-400" />
              <span className="text-xl font-bold">ShadowGuard</span>
            </div>

            <div className="flex gap-6">
              <a href="https://github.com" className="flex items-center gap-2 text-gray-400 hover:text-emerald-400 transition-colors">
                <Github className="w-5 h-5" />
                <span>GitHub Repo</span>
              </a>
              <a href="#" className="flex items-center gap-2 text-gray-400 hover:text-emerald-400 transition-colors">
                <FileText className="w-5 h-5" />
                <span>API Docs</span>
              </a>
              <a href="#" className="flex items-center gap-2 text-gray-400 hover:text-emerald-400 transition-colors">
                <Users className="w-5 h-5" />
                <span>Team Credits</span>
              </a>
            </div>
          </div>

          <div className="mt-8 text-center text-gray-500 text-sm">
            © 2025 ShadowGuard. Securing the Agentic AI Era.
          </div>
        </div>
      </footer>
    </div>
  );
}
