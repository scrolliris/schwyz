'use strict';

var path = require('path')
  , fs = require('fs')
  ;

var gulp = require('gulp')
  , env = require('gulp-env')
  , clean = require('gulp-clean')
  , rename = require('gulp-rename')
  , run = require('run-sequence')
  ;

var appName = 'puteoli';
var moduleDir = path.resolve(__dirname, 'node_modules/@lupine-software');

// -- [shared tasks]

gulp.task('env', function(done) {
  // loads environment vars from .env
  var dotenv_file = '.env';
  if (fs.existsSync(dotenv_file)) {
    return gulp.src(dotenv_file)
    .pipe(env({file: dotenv_file, type: '.ini'}));
  } else {
    return done();
  };
})

// -- [build tasks]

gulp.task('distribute:script', ['env'], function() {
  // copy tracker-browser.min.js.mako into static/dist
  var prefix = 'scrolliris-readability-';
  return gulp.src(
    moduleDir + '/' + prefix + 'tracker/dist/*-browser.min.js', {base: './'}
  )
  .pipe(rename(function(file) {
    file.dirname = 'dist';
    file.basename = file.basename.replace(new RegExp('^' + prefix), '');
    file.extname = '.js.mako';
  }))
  .pipe(gulp.dest('static'));
})

gulp.task('distribute:widget', ['env'], function() {
  // TODO
})

gulp.task('distribute:all', ['env'], function() {
  return gulp.start('distribute:script');
});

gulp.task('clean', function() {
  return gulp.src([
    'static/**/*.js.mako'
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
