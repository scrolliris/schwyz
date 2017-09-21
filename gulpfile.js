'use strict';

var path = require('path')
  , fs = require('fs')
  ;

var gulp = require('gulp')
  , env = require('gulp-env')
  , clean = require('gulp-clean')
  , rename = require('gulp-rename')
  , replace = require('gulp-replace')
  , run = require('run-sequence')
  ;

var moduleDir = path.resolve(__dirname, 'node_modules/@lupine-software')
  , prefix = 'scrolliris-readability-'
  ;

// -- [shared tasks]

gulp.task('env', function() {
  // loads environment vars from .env
  var dotenv_file = '.env';
  if (fs.existsSync(dotenv_file)) {
    return gulp.src(dotenv_file)
    .pipe(env({file: dotenv_file, type: '.ini'}));
  }
})

// -- [build tasks]

gulp.task('distribute:script', ['env'], function() {
  // copy tracker-browser.min.js.mako into static/dst
  var pkgName = prefix + 'tracker';
  return gulp.src([
    moduleDir + '/' + pkgName + '/dst/*-browser.min.js'
  ], {base: './'})
  .pipe(rename(function(file) {
    file.dirname = 'dst';
    file.basename = file.basename.replace(new RegExp('^' + prefix), '');
    file.extname += '.mako';
  }))
  .pipe(replace(/\.(csrfToken\|\|)null,/, '\.$1"${token}",'))
  .pipe(gulp.dest('static'));
})

gulp.task('distribute:widget', ['env'], function() {
  // copy reflector-{browser|canvas}.min.{css|js}.mako into static/dst
  var pkgName = prefix + 'reflector';
  return gulp.src([
    moduleDir + '/' + pkgName + '/dst/*-browser.min.js'
  , moduleDir + '/' + pkgName + '/dst/*-canvas.min.js'
  , moduleDir + '/' + pkgName + '/dst/*-canvas.min.css'
  ], {base: './'})
  .pipe(rename(function(file) {
    file.dirname = 'dst';
    file.basename = file.basename.replace(new RegExp('^' + prefix), '');
    file.extname += '.mako';
  }))
  .pipe(replace(/\|\|(\(o\.csrfToken=)""\);/, '\|\|$1"${token}"\);'))
  .pipe(gulp.dest('static'));
})

gulp.task('distribute:all', ['env'], function() {
  return run('distribute:script', 'distribute:widget');
});

gulp.task('clean', function() {
  return gulp.src([
    'static/**/*.js.mako'
  , 'static/**/*.css.mako'
  ], {
    read: false
  })
  .pipe(clean());
});

gulp.task('watch', ['env'], function() {
  gulp.watch('gulpfile.js', ['default']);
});


// -- [main tasks]

gulp.task('default', ['env'], function() {
  var nodeEnv = process.env.NODE_ENV || 'production';
  console.log('» gulp:', nodeEnv);

  return run('clean', 'distribute:all');
});
