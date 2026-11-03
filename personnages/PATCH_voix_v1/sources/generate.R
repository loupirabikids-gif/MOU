# Original PATCH recipes. Soundgen itself is GPL >= 2; no cloned voice.
args <- commandArgs(trailingOnly=TRUE)
out <- args[[1]]
dir.create(out, recursive=TRUE, showWarnings=FALSE)
library(soundgen)
common <- list(
 samplingRate=48000,pitchSamplingRate=48000,
 plot=FALSE,play=FALSE,saveAudio=FALSE,invalidArgAction='abort',
 addSilence=c(10,20),attackLen=c(20,50),
 formants=c(550,1400,2700,3900,4800),formantWidth=1.2,
 formantsNoise=NA,formantLocking=0,vocalTract=NA,
 rolloff=-26,rolloffNoise=-5,noiseFlatSpec=900,
 temperature=0.012,tempEffects=list(formDisp=0,formDrift=0),
 jitterDep=0.12,jitterLen=15,shimmerDep=2,shimmerLen=20,
 vibratoDep=0,subDep=0,glottis=0,lipRad=6,noseRad=3,
 mouthOpenThres=0.12)
recipes <- list(
 resolve_hm=list(sylLen=260,pitch=c(245,280,250),ampl=c(-10,0,-16),
  noise=-30,mouth=c(0.06,0.10,0.06),attackLen=c(25,55)),
 bored_exhale=list(sylLen=470,pitch=c(265,240,205),ampl=c(-3,-6,-24),
  noise=data.frame(time=c(0,100,470),value=c(-18,3,-17)),
  mouth=c(0.18,0.30,0.18),rolloff=-30,attackLen=c(30,90)),
 sleepy_yawn=list(sylLen=790,pitch=c(230,280,250,215),ampl=c(-15,-1,0,-20),
  noise=data.frame(time=c(0,170,490,790),value=c(-2,-16,-10,1)),
  mouth=c(0.12,0.65,0.85,0.12),rolloff=-29,attackLen=c(60,110),creakyBreathy=0.10),
 effort_small=list(sylLen=220,pitch=c(250,285,245),ampl=c(-9,0,-14),
  noise=-15,mouth=c(0.15,0.28,0.13),attackLen=c(20,55),rolloff=-27),
 surprise_inhale=list(sylLen=205,pitch=270,ampl=c(-12,0,-18),
  noise=data.frame(time=c(0,75,205),value=c(40,40,40)),
  mouth=c(0.18,0.60,0.30),attackLen=c(10,35),rolloffNoise=-4,jitterDep=0,shimmerDep=0,temperature=0),
 relief_chuckle=list(nSyl=2,sylLen=150,pauseLen=58,
  pitch=c(300,280),pitchGlobal=c(0,-1.0),ampl=c(-7,0,-14),amplGlobal=c(0,-3),
  noise=-9,mouth=c(0.25,0.50,0.25),attackLen=c(12,30),rolloff=-28,addSilence=c(10,50)))
for (id in names(recipes)) {
 for (variant in 1:2) {
  seed <- 7100+match(id,names(recipes))*10+variant
  set.seed(seed)
  pars <- modifyList(common,recipes[[id]])
  if (variant==2) {
   pars$pitch <- pars$pitch*1.035
   pars$jitterDep <- pars$jitterDep*1.1
  }
  x <- do.call(soundgen,pars)
  stopifnot(is.numeric(x),all(is.finite(x)),length(x)>0)
  stem <- paste0(id,'_',sprintf('%02d',variant))
  writeBin(as.double(x),file.path(out,paste0(stem,'.f64')),size=8,endian='little')
  dput(list(seed=seed,params=pars),file=file.path(out,paste0(stem,'.R')))
  cat(stem,length(x),'samples\n')
 }
}
writeLines(c(R.version.string,paste0('soundgen=',packageVersion('soundgen')),
 paste0('tuneR=',packageVersion('tuneR')),paste0('signal=',packageVersion('signal')),
 paste0('phonTools=',packageVersion('phonTools'))),file.path(out,'engine.txt'))
