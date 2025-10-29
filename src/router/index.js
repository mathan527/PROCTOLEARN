import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "../stores/auth"

// Pages
import LandingPage from "../pages/LandingPage.vue"
import LoginPage from "../pages/LoginPage.vue"
import RegisterPage from "../pages/RegisterPage.vue"
import StudentDashboard from "../pages/StudentDashboard.vue"
import TeacherDashboard from "../pages/TeacherDashboard.vue"
import TestInterface from "../pages/TestInterface.vue"
import TestCreation from "../pages/TestCreation.vue"
import TestCreationPage from "../pages/TestCreationPage.vue"
import TestJoinPage from "../pages/TestJoinPage.vue"
import ProctoringMonitor from "../pages/ProctoringMonitor.vue"
import ProctoringDashboard from "../pages/ProctoringDashboard.vue"
import AdminPanel from "../pages/AdminPanel.vue"
import ProfilePage from "../pages/ProfilePage.vue"
import CourseGenerator from "../pages/CourseGenerator.vue"
import GettingStarted from "../pages/GettingStarted.vue"
import NotFoundPage from "../pages/NotFoundPage.vue"
import ErrorPage from "../pages/ErrorPage.vue"
import WaitingRoom from "../pages/WaitingRoom.vue"
import StudentLearning from "../pages/StudentLearning.vue"

const routes = [
  { path: "/", component: LandingPage, meta: { requiresAuth: false } },
  { path: "/login", component: LoginPage, meta: { requiresAuth: false } },
  { path: "/register", component: RegisterPage, meta: { requiresAuth: false } },
  { path: "/getting-started", component: GettingStarted, meta: { requiresAuth: true } },
  { path: "/student/dashboard", component: StudentDashboard, meta: { requiresAuth: true, role: "student" } },
  { path: "/student/learning", component: StudentLearning, name: "StudentLearning", meta: { requiresAuth: true, role: "student" } },
  { path: "/student/test/:testId", component: TestInterface, meta: { requiresAuth: true, role: "student" } },
  { path: "/teacher/dashboard", component: TeacherDashboard, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/teacher/create-test", component: TestCreation, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/teacher/test-creation", component: TestCreationPage, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/teacher/monitor/:sessionId", component: ProctoringMonitor, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/teacher/proctoring/:testId", component: ProctoringDashboard, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/test-monitor/:testId", component: ProctoringMonitor, meta: { requiresAuth: true, role: "teacher" } },
  { path: "/course-generator", component: CourseGenerator, meta: { requiresAuth: true } },
  { path: "/join-test", component: TestJoinPage, meta: { requiresAuth: true } },
  { path: "/test/:testId", component: TestInterface, meta: { requiresAuth: true } },
  { path: "/waiting-room", component: WaitingRoom, meta: { requiresAuth: true } },
  { path: "/admin", component: AdminPanel, meta: { requiresAuth: true, role: "admin" } },
  { path: "/profile", component: ProfilePage, meta: { requiresAuth: true } },
  { path: "/error", component: ErrorPage },
  { path: "/:pathMatch(.*)*", component: NotFoundPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for auth and role-based access
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login")
  } else if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next("/error")
  } else {
    next()
  }
})

export default router
