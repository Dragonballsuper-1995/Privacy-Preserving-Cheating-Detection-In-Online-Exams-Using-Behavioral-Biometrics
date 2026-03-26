/**
 * Home Page - Exam Selection
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Terminal, Shield, Cpu, Activity, User, LogOut, ArrowRight, Clock, FileText, Lock } from 'lucide-react';
import { listExams, Exam, isAuthenticated, clearStoredToken, getCurrentUser } from '@/lib/api';
import { ThemeToggle } from '@/components/theme-toggle';

export default function HomePage() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    async function loadExams() {
      try {
        const data = await listExams();
        setExams(data.exams);
      } catch (err) {
        setError('SYSTEM_ERROR: FAILED_TO_CONNECT_TO_BACKEND');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadExams();

    // Check auth status
    if (isAuthenticated()) {
      setLoggedIn(true);
      getCurrentUser().then(user => {
        setUserName(user.full_name || user.email);
      }).catch(() => {
        // Token might be expired
        clearStoredToken();
        setLoggedIn(false);
      });
    }
  }, []);

  const handleLogout = () => {
    clearStoredToken();
    setLoggedIn(false);
    setUserName('');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 100 } }
  };

  return (
    <div className="min-h-screen text-foreground font-sans selection:bg-accent selection:text-background pb-20">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-border transition-colors duration-300">
        <div className="w-full mx-auto px-4 md:px-8 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-2 rounded-lg bg-primary text-primary-foreground shadow-sm">
              <Terminal className="w-8 h-8" />
            </div>
            <div>
              <h1 className="font-display text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
                Overseer Protocol
              </h1>
              <p className="font-sans text-xs text-muted-foreground uppercase tracking-wider font-semibold">
                Academic Integrity Matrix
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {loggedIn && userName && (
              <span className="font-mono text-sm font-bold uppercase hidden sm:block">
                SYS_ADMIN: {userName}
              </span>
            )}
            {loggedIn ? (
              <>
                <Link
                  href="/admin"
                  className="px-4 py-2 rounded-md font-sans text-sm font-semibold bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors flex items-center gap-2"
                  title="COMMAND CENTER"
                >
                  <Cpu className="w-4 h-4" />
                  <span className="hidden sm:inline">Portal</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-md font-sans text-sm font-semibold bg-destructive/10 text-destructive hover:bg-destructive hover:text-destructive-foreground transition-colors flex items-center gap-2"
                  title="TERMINATE SESSION"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-6 py-2 rounded-md bg-primary text-primary-foreground font-sans font-semibold hover:bg-primary/90 transition-colors shadow-sm"
              >
                <Lock className="w-4 h-4" />
                Auth Portal
              </Link>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="w-full mx-auto px-4 md:px-8 py-12 md:py-20">

        <div className="flex flex-col md:flex-row gap-12 items-start mb-16">
          <div className="md:w-1/2 space-y-6 sticky top-24">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/50 border border-primary/20 text-primary text-xs font-mono mb-4">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
              SYSTEM.STATUS: OPTIMAL
            </div>
            <h2 className="font-display text-5xl md:text-7xl font-bold tracking-tight leading-tight">
              Truth,
              <br />
              Detected by
              <br />
              <span className="text-primary glow-text">Pure Intelligence.</span>
            </h2>
            <p className="font-sans text-lg text-muted-foreground max-w-xl border-l-4 border-primary pl-4">
              The nexus of academic integrity. No cameras. No privacy invasions. Just absolute certainty powered by behavioral heuristics and algorithmic analysis.
            </p>
            <div className="flex gap-4 pt-4">
              <Link href="/login" className="px-8 py-3 rounded-full bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(195,180,253,0.3)]">
                Initialize Core
              </Link>
              <a href="#features" className="px-8 py-3 rounded-full bg-secondary text-secondary-foreground font-semibold hover:bg-secondary/80 transition-all border border-border inline-flex items-center gap-2">
                View Specs
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>

          <div className="md:w-1/2 w-full">
            {/* Error state */}
            {error && (
              <div className="mb-6 p-6 rounded-xl bg-destructive/10 text-destructive border border-destructive/20 shadow-sm">
                <p className="font-sans font-semibold mb-2 flex items-center gap-2">
                  <Terminal className="w-5 h-5" />
                  {error}
                </p>
                <p className="font-mono text-xs opacity-80">
                  ACTIVATE BACKEND: uvicorn app.main:app --reload
                </p>
              </div>
            )}

            {/* Loading state */}
            {loading && (
              <div className="flex justify-center p-20">
                <div className="w-10 h-10 border-4 border-muted border-t-primary rounded-full animate-spin" />
              </div>
            )}

            {/* Exams Data Matrix */}
            {!loading && !error && (
              <div className="space-y-6 glass-panel p-6 relative overflow-hidden">
                <div className="absolute inset-0 bg-cyber-grid pointer-events-none opacity-20"></div>
                <div className="absolute inset-x-0 h-px bg-primary/40 animate-scan-line shadow-[0_0_10px_rgba(195,180,253,0.5)]"></div>
                <div className="relative z-10 flex items-center justify-between border-b border-border/50 pb-4">
                  <h2 className="font-display text-2xl font-semibold tracking-tight flex items-center gap-3">
                    <FileText className="w-6 h-6 text-primary" />
                    Available Exams
                  </h2>
                  <span className="font-sans text-xs font-semibold bg-secondary text-secondary-foreground rounded-full px-3 py-1">
                    {exams.length} Nodes
                  </span>
                </div>

                <div className="max-h-[600px] overflow-y-auto pr-4 custom-scrollbar">
                  <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-2 gap-4"
                  >
                    {exams.length === 0 ? (
                      <div className="col-span-full py-16 text-center border border-dashed border-border rounded-xl">
                        <p className="font-sans text-lg font-medium text-muted-foreground">No active assessments detected.</p>
                      </div>
                    ) : (
                      exams.map((exam) => (
                        <motion.div
                          key={exam.id}
                          variants={itemVariants}
                          className="group bg-card rounded-xl border border-border flex flex-col hover:shadow-lg transition-all hover:-translate-y-1 overflow-hidden"
                        >
                          <div className="h-2 w-full bg-primary/20 transition-all group-hover:bg-primary" />
                          <div className="p-5 flex-1 flex flex-col">
                            <h3 className="font-display text-xl font-semibold tracking-tight mb-2">
                              {exam.title}
                            </h3>
                            <p className="font-sans text-sm text-muted-foreground mb-4 flex-1 line-clamp-2">
                              {exam.description || 'No description provided.'}
                            </p>

                            <div className="flex items-center gap-4 mb-4 font-sans text-xs font-medium py-3 border-y border-border">
                              <div className="flex items-center gap-2 text-muted-foreground">
                                <Clock className="w-4 h-4 text-primary" />
                                <span>{exam.duration_minutes} min</span>
                              </div>
                              <div className="w-1 h-1 bg-border rounded-full" />
                              <div className="flex items-center gap-2 text-muted-foreground">
                                <FileText className="w-4 h-4 text-primary" />
                                <span>{exam.question_count} nodes</span>
                              </div>
                            </div>

                            <Link
                              href={`/exam/${exam.id}`}
                              className="w-full py-2.5 rounded-lg flex items-center justify-center gap-2 bg-secondary text-secondary-foreground font-sans font-semibold hover:bg-primary hover:text-primary-foreground transition-colors group/btn"
                            >
                              Initiate
                              <ArrowRight className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" />
                            </Link>
                          </div>
                        </motion.div>
                      ))
                    )}
                  </motion.div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Feature Boxes */}
        <div id="features" className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="p-8 glass-panel hover:shadow-lg transition-all hover:-translate-y-1">
            <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center mb-6">
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-sans text-xl font-semibold mb-3">Privacy First</h3>
            <p className="font-sans text-muted-foreground leading-relaxed">No camera or microphone required. Silent detection via advanced keyboard telemetry and algorithmic behavioral analysis, completely protecting user environments while maintaining rigorous integrity standards.</p>
          </div>
          <div className="p-8 glass-panel relative overflow-hidden border-primary/30 hover:shadow-[0_0_30px_rgba(195,180,253,0.15)] transition-all hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl"></div>
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-6 relative z-10">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-sans text-xl font-semibold mb-3 relative z-10">Neural Analysis</h3>
            <p className="font-sans text-muted-foreground leading-relaxed relative z-10">AI models continuously monitor typing cadence, hesitation metrics, clipboard activities, and browser focus loss events in real-time to detect anomalous behavioral patterns and provide a deterministic risk quotient.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
