import { Router, type IRouter } from "express";
import healthRouter from "./health";
import authRouter from "./auth";
import documentsRouter from "./documents";
import searchRouter from "./search";
import askRouter from "./ask";
import communityRouter from "./community";
import studyRouter from "./study";

const router: IRouter = Router();

router.use(healthRouter);
router.use(authRouter);
router.use(documentsRouter);
router.use(searchRouter);
router.use(askRouter);
router.use(communityRouter);
router.use(studyRouter);

export default router;
