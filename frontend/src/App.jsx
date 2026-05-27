import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "./components/navbar";

const App = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen">
      {/* Navbar is shown on all pages */}
      <Navbar />

      {/* Page transition wrapper */}
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Outlet />
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default App;
