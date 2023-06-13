<?php

declare(strict_types=1);

$finder = PhpCsFixer\Finder::create()
	->in(__DIR__)
	->exclude('.git')
	->exclude('vendor');

$config = new PhpCsFixer\Config();

return $config
	->setRiskyAllowed(true)
	->setIndent("\t")
	->setLineEnding("\n")
	// ->setUsingCache(true)
	// ->setCacheFile(__DIR__.'/.php-cs-fixer.cache')
	->setRules([
		'@PHP81Migration' => true,
		'@PHP80Migration:risky' => true,
		// "@PHPUnit84Migration:risky" => true,
		'@PhpCsFixer' => true,
		'@PhpCsFixer:risky' => true,
		'braces' => [
			'allow_single_line_anonymous_class_with_empty_body' => true,
			'allow_single_line_closure' => true,
			'position_after_functions_and_oop_constructs' => 'same',
			'position_after_control_structures' => 'same',
			'position_after_anonymous_constructs' => 'same',
		],
		'multiline_whitespace_before_semicolons' => [
			'strategy' => 'no_multi_line',
		],
	])
	->setFinder($finder);
