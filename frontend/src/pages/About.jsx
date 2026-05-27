import { useState } from "react";
import { Link } from "react-router-dom";
import logo from "/src/assets/images/logo.svg";

export default function About() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <div className="min-h-screen bg-gradient-to-r from-[#0e001d] via-[#1a0733] to-[#3d2171] text-white pb-20">

      {/* About Section */}
      <div className="pt-28 px-8 md:px-24 max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-6">About IITI Bot</h1>
        <p className="mb-4">
          <strong>IITI Bot</strong> is your all-in-one assistant for exploring
          everything about
          <strong> IIT Indore</strong> — from academics, research, and clubs to
          sports, fests, tech events, hostel life, and more.
        </p>
        <p className="mb-8">
          Designed for students, faculty, aspirants, and anyone curious about
          IIT Indore, this bot provides accurate, real-time answers to questions
          across domains using natural language conversations.
        </p>

        <h2 className="text-xl font-semibold text-purple-300 mt-10 mb-2">
          What Can IITI Bot Do?
        </h2>
        <ul className="list-disc list-inside space-y-2 text-gray-200">
          <li>Answer queries about departments, courses, and academics</li>
          <li>Provide details on campus life, events, and hostel facilities</li>
          <li>Fetch updates on fests, sports activities, and student clubs</li>
          <li>Assist new joiners and aspirants with relevant information</li>
        </ul>

        <h2 className="text-xl font-semibold text-purple-300 mt-10 mb-2">
          How It Works
        </h2>
        <p className="mb-4">
          IITI Bot is powered by a{" "}
          <strong>Retrieval-Augmented Generation (RAG)</strong> architecture
          using the <strong>Pathway</strong> stream processing framework for
          real-time web search and knowledge retrieval. It integrates:
        </p>
        <ul className="list-disc list-inside space-y-2 text-gray-200">
          <li>
            <strong>FastAPI</strong> – Lightweight Python backend framework
          </li>
          <li>
            <strong>HTML, CSS, JS</strong> – For responsive and dynamic UI
          </li>
          <li>
            <strong>LLMs</strong> – To understand and generate accurate answers
          </li>
          <li>
            <strong>Live web tools</strong> – To keep responses up-to-date
          </li>
        </ul>

        <h2 className="text-xl font-semibold text-purple-300 mt-10 mb-2">
          Contact Us
        </h2>
        <p>
          Got suggestions or questions? Drop us an email at:{" "}
          <a
            href="mailto:chitkararudra946@gmail.com"
            className="text-blue-300 underline"
          >
            chitkararudra946@gmail.com
          </a>
        </p>
      </div>
    </div>
  );
}
