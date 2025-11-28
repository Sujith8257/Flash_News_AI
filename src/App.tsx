import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Home } from "./pages/Home"
import { Feed } from "./pages/Feed"
import { Article } from "./pages/Article"
import { SignIn } from "./pages/SignIn"
import { SignUp } from "./pages/SignUp"
import { About } from "./pages/About"
import { Features } from "./pages/Features"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/article" element={<Article />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/about" element={<About />} />
        <Route path="/features" element={<Features />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

