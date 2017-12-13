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
  // use @lupine-software/scrolliris-readability-tracker
  // schwyz provides /measure.js

  // -- measure
  // copy tracker-browser.min.js into static/dst
  // as `measure-browser.min.js.mako`
  var pkgName = prefix + 'tracker';
  return gulp.src([
    moduleDir + '/' + pkgName + '/dst/*-browser.min.js'
  ], {base: './'})
  .pipe(rename(function(file) {
    file.dirname = 'dst';
    file.basename = file.basename.replace(
      new RegExp('^' + pkgName), 'measure');
    file.extname += '.mako';
  }))
  .pipe(replace(/\.(csrfToken\|\|)null,/, '\.$1"${token}",'))
  .pipe(gulp.dest('static'));
})

gulp.task('distribute:widget', ['env'], function() {
  // use @lupine-software/scrolliris-readability-reflector
  // schwyz provides /heatmap.js (type: minimap|overlay)

  // -- minimap
  // copy reflector-browser.js and
  // reflector-{minimap|overlay}.min.{css|js} into static/dst
  // as `heatmap-{browser|minimap}.min.{css|js}.mako`
  var pkgName = prefix + 'reflector';
  return gulp.src([
    moduleDir + '/' + pkgName + '/dst/*-browser.min.js'
  , moduleDir + '/' + pkgName + '/dst/*-minimap.min.js'
  , moduleDir + '/' + pkgName + '/dst/*-minimap.min.css'
  ], {base: './'})
  .pipe(rename(function(file) {
    file.dirname = 'dst';
    file.basename = file.basename.replace(
      new RegExp('^' + pkgName), 'heatmap');
    file.extname += '.mako';
  }))
  .pipe(replace(/\|\|(\(o\.csrfToken=)""\);/, '\|\|$1"${token}"\);'))
  .pipe(gulp.dest('static'));
  // -- overlay
  // hreturn gulp.src([
  //   moduleDir + '/' + pkgName + '/dst/*-browser.min.js'
  // , moduleDir + '/' + pkgName + '/dst/*-overlay.min.js'
  // , moduleDir + '/' + pkgName + '/dst/*-overlay.min.css'
  // ], {base: './'})
  // ...
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
