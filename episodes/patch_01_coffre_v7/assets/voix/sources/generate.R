# Original PATCH V2: a squeaky source/filter identity and distinct articulations.
# Soundgen is GPL >= 2. Original project recipes have no new public licence.
args <- commandArgs(trailingOnly=TRUE)
out <- args[[1]]
dir.create(out, recursive=TRUE, showWarnings=FALSE)
library(soundgen)
common <- list(
 samplingRate=48000,pitchSamplingRate=48000,
 plot=FALSE,play=FALSE,saveAudio=FALSE,invalidArgAction='abort',
 addSilence=c(10,20),attackLen=c(16,45),
 formants=c(715,1820,3510,5070,6240),formantWidth=1.35,
 formantsNoise=NA,formantLocking=0,vocalTract=11,
 rolloff=-20,rolloffNoise=-7,noiseFlatSpec=900,
 temperature=0.012,tempEffects=list(formDisp=0,formDrift=0),
 jitterDep=0.30,jitterLen=12,shimmerDep=3,shimmerLen=18,
 vibratoDep=0,subDep=0,glottis=0,lipRad=5.5,noseRad=3.5,
 mouthOpenThres=0.12)
recipes <- list(
 resolve_hm=list(nSyl=2,sylLen=115,pauseLen=40,
  pitch=c(500,585,545),pitchGlobal=c(0,2),ampl=c(-8,0,-16),
  amplGlobal=c(-3,0),noise=-26,mouth=c(0.04,0.08,0.05),
  attackLen=c(14,30),addSilence=c(10,25)),
 bored_exhale=list(sylLen=470,pitch=c(650,530,390),ampl=c(-2,-6,-24),
  noise=data.frame(time=c(0,100,260,470),value=c(-14,-3,12,8)),
  mouth=c(0.16,0.32,0.22),rolloff=-25,attackLen=c(25,95)),
 sleepy_yawn=list(sylLen=790,pitch=c(440,580,700,480),ampl=c(-16,-3,0,-20),
  noise=data.frame(time=c(0,160,470,790),value=c(5,-13,-8,9)),
  mouth=c(0.13,0.50,0.92,0.13),rolloff=-23,attackLen=c(65,120),
  creakyBreathy=0.12),
 effort_small=list(sylLen=205,pitch=c(450,660,490),ampl=c(-12,0,-20),
  noise=-13,mouth=c(0.15,0.40,0.13),attackLen=c(14,40),
  rolloff=-21,creakyBreathy=-0.10),
 surprise_inhale=list(sylLen=190,pitch=c(520,810,680),ampl=c(-5,0,-22),
  noise=data.frame(time=c(0,45,95,190),value=c(40,20,3,20)),
  mouth=c(0.18,0.67,0.34),attackLen=c(8,35),rolloff=-22,
  rolloffNoise=-7,jitterDep=0.15,shimmerDep=1),
 relief_chuckle=list(nSyl=2,sylLen=140,pauseLen=68,
  pitch=c(760,690,570),pitchGlobal=c(0,2.0),ampl=c(-8,0,-18),
  amplGlobal=c(0,-3),noise=-7,mouth=c(0.26,0.64,0.31),
  attackLen=c(12,32),rolloff=-21,addSilence=c(10,40)))
for (id in names(recipes)) {
 for (variant in 1:2) {
  seed <- 8200+match(id,names(recipes))*10+variant
  set.seed(seed)
  pars <- modifyList(common,recipes[[id]])
  if (variant==2) {
   pars$pitch <- pars$pitch*1.04
   pars$jitterDep <- pars$jitterDep*1.15
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
