import { motion } from 'framer-motion';
import { Shield, Bot, Lock, Zap, Database, Bell, ArrowRight, Github, FileText, Users } from 'lucide-react';
import { GlassCard } from './GlassCard';
import { FloatingCard } from './FloatingCard';
import { SimulationConsole } from './SimulationConsole';

export function LandingPage() {
  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 py-20">
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-radial from-emerald-900/20 via-black to-black"></div>
        
        {/* Floating decorative elements */}
        <div className="absolute top-1/4 left-1/4 hidden lg:block">
          <FloatingCard delay={0} duration={4}>
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Shadow AI Detected</span>
            </div>
          </FloatingCard>
        </div>

        <div className="absolute top-1/3 right-1/4 hidden lg:block">
          <FloatingCard delay={1} duration={5}>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Data Exfiltration Blocked</span>
            </div>
          </FloatingCard>
        </div>

        <div className="absolute bottom-1/3 left-1/3 hidden lg:block">
          <FloatingCard delay={2} duration={4.5}>
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Compliance Verified</span>
            </div>
          </FloatingCard>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-block mb-6">
              <span className="px-4 py-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm font-medium">
                Solutions
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="text-gray-200">Secure the</span>
              <br />
              <span className="hero-glow">Agentic AI Era</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto">
              Real-time detection of unauthorized GenAI, data leaks, and shadow SaaS usage in your corporate network.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => scrollToSection('simulation')}
                className="btn-primary group"
              >
                <span>Launch Simulation</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => scrollToSection('architecture')}
                className="btn-secondary"
              >
                View Architecture
              </button>
            </div>
          </motion.div>
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
            {/* Visual */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-emerald-500/20 via-black to-black border border-emerald-500/20 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-emerald-500/30 via-transparent to-transparent"></div>
                <div className="relative z-10">
                  <Shield className="w-32 h-32 text-emerald-400 animate-pulse" />
                </div>
                <div className="absolute top-1/4 left-1/4 w-16 h-16 rounded-full bg-emerald-500/20 blur-xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-24 h-24 rounded-full bg-emerald-500/10 blur-2xl"></div>
              </div>
            </motion.div>

            {/* Threat List */}
            <div className="space-y-4">
              <GlassCard delay={0.1}>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <span className="text-red-400">›</span> Inserting Backdoors in AI Models
                  </h3>
                  <p className="text-gray-400">Malicious actors compromise model integrity</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.2}>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <span className="text-red-400">›</span> Extraction of AI Models and Data
                  </h3>
                  <p className="text-gray-400">Sensitive IP leaked through unapproved channels</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.3}>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <span className="text-red-400">›</span> Jailbreaks & Model DoS Attacks
                  </h3>
                  <p className="text-gray-400">Bypassing safety measures and overwhelming systems</p>
                </div>
              </GlassCard>

              <GlassCard delay={0.4}>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <span className="text-red-400">›</span> Social Engineering & Misalignment
                  </h3>
                  <p className="text-gray-400">Manipulating AI outputs for malicious purposes</p>
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
              Verifiable Compute <span className="text-emerald-400">Verifies</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-3xl mx-auto">
              Introducing Verifiable Compute. Ready for the Agentic AI Era.
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
