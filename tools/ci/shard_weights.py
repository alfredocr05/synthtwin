"""How long each test file takes, for packing the CI shards.

MEASURED, NOT GUESSED. Every number below is one file's own share of a
single ordinary `pytest -q --durations=0` run of the whole suite on the
reference machine the KPI ledger names (Apple M4, ten cores): the
setup, call and teardown seconds of its cases, added up. That is the
cost a shard inherits when it takes the file, its module-scoped
fixtures included. Interpreter start and collection are left out: a
shard is charged for those once, however many files it holds.

TO RE-MEASURE, on a quiet reference machine:

    .venv/bin/python -m pytest -q --durations=0 > durations.txt

and add up, per file, the seconds it prints against each case.

RE-MEASURED 2026-10-01 (plan P4-D364). Every row below is one file's
seconds from the five shards of one whole-suite run of `622159b` through
the machine-wide lock with `--durations=0`: each shard a process of its
own, the five at once, on a machine other work was loading. Running
five at once inflates every file about alike, and the packing reads only
which file outweighs which. The table had last been measured before
stage 3b: the stage 3b gate stood at 80 seconds and every file added
since weighed the default, so the third shard ran long.

WHAT A STALE NUMBER COSTS, AND WHAT IT CANNOT COST. These seconds
decide only the PACKING: which shard a file lands in. A number that has
drifted makes one shard longer than another and never makes a file run
twice or not at all -- `tools/ci/shards.py --prove` is what holds that,
against pytest's own collection. So this table is a convenience that
may be re-measured whenever somebody wants the shards to come out
closer in length, and it is never a thing a test result depends on.

SEVEN ROWS ADDED 2026-10-08, at the integration of wave 2's first batch:
the test files its lanes added (and lane G3's count pass file, which had
none), each timed ON ITS OWN -- one `pytest -q --durations=0` process per
file on the integrated tree, on a machine other work was loading -- and summed as
above. A file timed alone runs a little faster than beside four other
shards, so these weigh it a little light; the packing reads only which
file outweighs which.

FOUR ROWS ADDED 2026-10-09, at the integration of wave 2's batch 2a:
the test files its lanes added (R2a's layout file, G4's counts per
block, T2's hour file and its review's), each timed ON ITS OWN on the
integrated tree as the seven above were, on a machine other work was
loading.

ONE ROW ADDED AND ONE RE-MEASURED 2026-10-09, at the integration of
the route-2 correction, each file timed on its own on the integrated
tree: the correction's own file 26.16 s, and the clock review's file
127.11 s, which round 2 of landing 3b.5's review took from 14.83 s.

ROWS ADDED 2026-10-12, at the integration of batch 2b's first part:
the test files its lanes added, each timed ON ITS OWN on the integrated
tree as above, on a machine other work was loading -- lane D2's weekday
census of moments, 78.96 s, and lane S4a's sign repairs, 18.92 s.

ROWS ADDED 2026-10-12, at the integration of batch 2b's second part,
each file timed ON ITS OWN on the integrated tree as above, on a machine
other work was loading: lane R4's two files, numbers that are dates,
213.21 s and its Codex review's 71.62 s, and lane D0's shared steps,
26.37 s, which had had no row since it landed.

A FILE WITH NO ROW weighs `DEFAULT_SECONDS`. Two kinds of file have
none: one added since the last measurement, which is then placed like
an ordinary small file and runs in its shard from the commit that adds
it; and one every case of which fell under the five milliseconds pytest
prints a duration for at all, which is a file the default overstates
and which costs the packing nothing worth another decimal.
"""

# The weight of a test file this table has no measurement for: a little
# over the median file, so a handful of new files cannot all land in one
# shard by looking free.
DEFAULT_SECONDS = 2.0

SECONDS = {
    "tests/test_ap311_lowered_floor.py": 22.69,
    "tests/test_ap312_fold_repair.py": 198.16,
    "tests/test_ap313_stated_limit.py": 0.56,
    "tests/test_ap326_unrebuildable_reading_rule.py": 3.12,
    "tests/test_ap329_reading_rule_from_version_5.py": 3.17,
    "tests/test_carried_numbers.py": 10.07,
    "tests/test_census_reading_handed_over.py": 1.32,
    "tests/test_ci_demo_steps.py": 1.46,
    "tests/test_ci_shards.py": 0.07,
    "tests/test_claim_inventory.py": 21.1,
    "tests/test_cli_generate.py": 2.52,
    "tests/test_cli_profile.py": 8.87,
    "tests/test_cli_validate.py": 16.97,
    "tests/test_column_analysis.py": 11.22,
    "tests/test_column_analysis_extra.py": 0.3,
    "tests/test_commit_messages.py": 4.26,
    "tests/test_commonest_width_grid.py": 3.1,
    "tests/test_contract_loader.py": 8.65,
    "tests/test_contract_self_check.py": 1.95,
    "tests/test_date_spread.py": 448.08,
    "tests/test_dates_written_forms_disclosed.py": 15.56,
    "tests/test_decontamination.py": 664.17,
    "tests/test_dependencies.py": 2.24,
    "tests/test_description_line_endings.py": 11.42,
    "tests/test_extra_review_dates.py": 76.55,
    "tests/test_extra_round_disclosure.py": 52.55,
    "tests/test_extra_round_numbers.py": 5.56,
    "tests/test_failure_catalog.py": 1.06,
    "tests/test_file_dialect_round_trip.py": 52.17,
    "tests/test_files_review_2026_09_18.py": 7.52,
    "tests/test_files_review_repairs.py": 15.83,
    "tests/test_final_review_labels.py": 28.64,
    "tests/test_final_skeptic_repairs.py": 18.68,
    "tests/test_generation.py": 7.12,
    "tests/test_generation_reference.py": 95.29,
    "tests/test_held_unit_search.py": 25.61,
    "tests/test_joined_battery_readings.py": 215.32,
    "tests/test_joined_pair_round_trip.py": 103.91,
    "tests/test_k_p3_03_outer_tail_spread.py": 58.33,
    "tests/test_kpi_ledger.py": 658.49,
    "tests/test_kpi_ledger_integrity.py": 9.84,
    "tests/test_landing_2b12_identifiers_codes_text.py": 15.77,
    "tests/test_landing_2b13_numbers_beside_labels.py": 5.74,
    "tests/test_landing_2b15_unanchored_numbers.py": 8.18,
    "tests/test_landing_2b16_number_readings.py": 57.37,
    "tests/test_landing_2b18_forms_and_spellings.py": 50.39,
    "tests/test_landing_2b18_identifier_layout.py": 96.4,
    "tests/test_landing_2b18_layout_disclosure.py": 35.17,
    "tests/test_landing_2b2_number_spellings.py": 147.82,
    "tests/test_landing_2b7_mixed_spellings.py": 19.23,
    "tests/test_landing_2b7_source_spellings.py": 41.25,
    "tests/test_landing_2b8_labels_text_missing.py": 101.84,
    "tests/test_lone_figure_nought.py": 0.15,
    "tests/test_lone_pools_every_reader.py": 17.86,
    "tests/test_merge_close_2026_09_18.py": 8.38,
    "tests/test_method_citations_resolve.py": 0.48,
    "tests/test_mixture_reader_bounds.py": 78.4,
    "tests/test_moment_window_anchor.py": 11.3,
    "tests/test_no_quadratic_list_growth.py": 2.35,
    "tests/test_number_censuses_name_no_row.py": 26.27,
    "tests/test_numbers_beside_labels.py": 45.32,
    "tests/test_numeric_strata_round_trip.py": 380.36,
    "tests/test_offline_scan.py": 7.37,
    "tests/test_older_censuses_name_no_row.py": 12.86,
    "tests/test_oracle_proof_layer.py": 1.05,
    "tests/test_oracle_rule_witnesses.py": 51.37,
    "tests/test_p1r6f11_display_boundary.py": 0.26,
    "tests/test_p1r6f4_comprehension_scopes.py": 5.94,
    "tests/test_p1r6f6_first_row_decision.py": 1.32,
    "tests/test_p1r6f7_one_policy.py": 20.56,
    "tests/test_p1r6f8_identifier_evidence.py": 21.36,
    "tests/test_p1r6f9_declared_values.py": 2.13,
    "tests/test_p1r7f1_any_exception.py": 0.05,
    "tests/test_p1r7f1_transaction_disclosure.py": 0.07,
    "tests/test_p1r7f2_declaration_disclosure.py": 0.81,
    "tests/test_p1r7f2_disclosure_is_true.py": 1.16,
    "tests/test_p1r7f2_withholding_block.py": 1.35,
    "tests/test_p1r7f3_exact_declarations.py": 5.09,
    "tests/test_p1r8f1_guard_seam.py": 2.77,
    "tests/test_p1r8f1_working_name_claim.py": 1.95,
    "tests/test_p1r8f2_exact_sentinels.py": 2.5,
    "tests/test_p1r8f4_repetition_multiset.py": 0.2,
    "tests/test_p2c1f2_invention_domain.py": 0.23,
    "tests/test_p2c1f3_publication_guard.py": 19.75,
    "tests/test_p2c1f4_approximation_bounds.py": 4.21,
    "tests/test_p2c1f5_leading_zero_family.py": 214.54,
    "tests/test_p2c1f6_temporal_round_trip.py": 0.51,
    "tests/test_p2c1f8_specification_agreement.py": 0.5,
    "tests/test_p2c2f1_complete_allocation.py": 121.91,
    "tests/test_p2c2f2_style_placement.py": 0.15,
    "tests/test_p2c2f3_style_invention.py": 0.21,
    "tests/test_p2c2f4_numeric_cardinality_bounds.py": 0.24,
    "tests/test_p2c2f5_temporal_endpoints.py": 40.82,
    "tests/test_p2c2f6_fold_collisions.py": 0.17,
    "tests/test_p2c2f8_invention_walk_bound.py": 0.02,
    "tests/test_p2c3f1_published_margins.py": 9.54,
    "tests/test_p2c4f1_disposition_registry.py": 15.27,
    "tests/test_p2c4f2_text_shape.py": 50.92,
    "tests/test_p2c4f3_style_capacity.py": 41.98,
    "tests/test_p2c5f2_identifier_classes.py": 272.55,
    "tests/test_p2c5f3_style_reach.py": 74.88,
    "tests/test_p2c5f4_generation_refusals.py": 4.74,
    "tests/test_p2d10_artifact_words.py": 0.02,
    "tests/test_p3_flip_migration.py": 0.34,
    "tests/test_p3v10f3_the_walk_stops_at_the_tables_keys.py": 0.79,
    "tests/test_p3v10f4_named_markers_are_holes.py": 1.29,
    "tests/test_p3v10f5_exact_equality_wins.py": 24.34,
    "tests/test_p3v11f2_no_refusal_quotes_your_spelling.py": 0.79,
    "tests/test_p3v12f2_a_miss_says_what_it_found.py": 21.9,
    "tests/test_p3v1f12_one_target_transaction.py": 1.91,
    "tests/test_p3v1f2_entry_table.py": 779.79,
    "tests/test_p3v2a1_presence_split.py": 1864.26,
    "tests/test_p3v3f1_description_equivalence.py": 78.83,
    "tests/test_p3v3f3_refused_files.py": 2.55,
    "tests/test_p3v3f4_ordinal_spaces.py": 17.81,
    "tests/test_p3v3f5_written_form.py": 2.05,
    "tests/test_p3v3f6_reader_agreement.py": 10.53,
    "tests/test_p3v4f10_windows_reach.py": 4.08,
    "tests/test_p3v4f1_kept_values.py": 102.15,
    "tests/test_p3v4f2_canonical_ceiling.py": 4.17,
    "tests/test_p3v4f3_refusal_equivalence.py": 1.11,
    "tests/test_p3v4f4_datetime_windows.py": 2.75,
    "tests/test_p3v5f1_floor_one.py": 65.55,
    "tests/test_p3v6f1_identifier_corner.py": 0.6,
    "tests/test_p3v7f1_escaped_declarations.py": 1.89,
    "tests/test_p3v7f2_corner_parity.py": 32.71,
    "tests/test_p3v8f5_published_keys.py": 36.62,
    "tests/test_p3v9f1_declared_words_disclosed.py": 0.35,
    "tests/test_p3v9f2_one_key_space.py": 0.28,
    "tests/test_p3v9f3_escaping_is_display_only.py": 0.71,
    "tests/test_p3v9f4_declarations_not_keys.py": 1.22,
    "tests/test_p3v9f5_sentinels_settle.py": 1.27,
    "tests/test_p3v9f6_migration_names_every_option.py": 0.83,
    "tests/test_p3v9f7_declarations_not_keystrokes.py": 0.6,
    "tests/test_p4a1_calendar_placeholders.py": 94.4,
    "tests/test_p4a58_asking_shapes.py": 2.68,
    "tests/test_p4a60_answers_handed_back.py": 3.07,
    "tests/test_p4d140_number_censuses.py": 104.88,
    "tests/test_p4d14_pad_widths.py": 2.53,
    "tests/test_p4d15_dotted_and_two_digit_dates.py": 12.95,
    "tests/test_p4d15_textual_dates.py": 2.41,
    "tests/test_p4d16_padded_numbers.py": 0.89,
    "tests/test_p4d17_group_commas.py": 3.46,
    "tests/test_p4d182_layout_packing.py": 8.94,
    "tests/test_p4d184_joined_value_counts.py": 16.78,
    "tests/test_p4d185_grouped_cells.py": 14.08,
    "tests/test_p4d186_title_rows.py": 1.91,
    "tests/test_p4d187_numbers_stored_as_text.py": 1.8,
    "tests/test_p4d188_sheet_names_in_the_report.py": 0.98,
    "tests/test_p4d189_format_codes_as_written.py": 16.44,
    "tests/test_p4d18_role_topology.py": 0.08,
    "tests/test_p4d18_shape_forms.py": 12.01,
    "tests/test_p4d190_numbers_carry_the_average.py": 4.29,
    "tests/test_p4d191_p4d192_date_counts.py": 19.34,
    "tests/test_p4d193_twice_written_wholes.py": 11.7,
    "tests/test_p4d194_signed_marks.py": 18.42,
    "tests/test_p4d195_width_conventions_named.py": 7.4,
    "tests/test_p4d196_identifier_layout_partners_signs.py": 4.19,
    "tests/test_p4d197_stored_as_text_withheld.py": 4.31,
    "tests/test_p4d198_truth_values_written.py": 20.16,
    "tests/test_p4d19_declared_codes.py": 2.46,
    "tests/test_p4d21_joined_numbers.py": 14.56,
    "tests/test_p4d230_prefixed_partners_wear_named_layouts.py": 2.75,
    "tests/test_p4d233_hexadecimal_prefix.py": 5.97,
    "tests/test_p4d239_forced_counts_of_one.py": 16.98,
    "tests/test_p4d241_record_shape_names_no_column.py": 3.85,
    "tests/test_p4d242_commonest_written_name.py": 0.15,
    "tests/test_p4d243_comma_shape_forms.py": 99.07,
    "tests/test_p4d244_made_up_can_coincide.py": 0.7,
    "tests/test_p4d26_contract_describes_the_producer.py": 0.03,
    "tests/test_p4d26_decimal_comma.py": 6.21,
    "tests/test_p4d27_address_remark.py": 3.93,
    "tests/test_p4d27_note_grammar_matches_the_code.py": 0.09,
    "tests/test_p4d27_token_not_quantity.py": 0.21,
    "tests/test_p4d28_free_text_keeps_its_kind.py": 2.2,
    "tests/test_p4d291_dates_a_reader_opens.py": 4.24,
    "tests/test_p4d298_absorbed_readings.py": 1.02,
    "tests/test_p4d2_loud_decline.py": 1.26,
    "tests/test_p4d30_field_widths.py": 2.47,
    "tests/test_p4d32_empty_bins.py": 38.7,
    "tests/test_p4d334_sentence_arguments.py": 227.97,
    "tests/test_p4d341_population_floor.py": 15.63,
    "tests/test_p4d349_tail_reconstruction.py": 9.54,
    "tests/test_p4d353_cost_rule.py": 176.89,
    "tests/test_p4d357_review_of_followup_a.py": 133.96,
    "tests/test_p4d361_compared_reaches.py": 701.85,
    "tests/test_p4d390_counts_per_block.py": 144.64,
    "tests/test_p4d411_mode.py": 0.88,
    "tests/test_p4d42_clock_role.py": 6.95,
    "tests/test_p4d43_date_readings.py": 3.82,
    "tests/test_p4d44_unrepresentable_widths.py": 10.93,
    "tests/test_p4d46_day_first.py": 0.33,
    "tests/test_p4d48_kurtosis.py": 0.18,
    "tests/test_p4d4_affixed_role.py": 18.44,
    "tests/test_p4d5_long_tail_labels.py": 9.11,
    "tests/test_p4d61_holes_reproduced.py": 52.1,
    "tests/test_p4d62_machine_artifacts.py": 0.39,
    "tests/test_p4d64_judged_stand_ins_written.py": 63.25,
    "tests/test_p4g3r1_joined_review.py": 55.76,
    "tests/test_p4r13_compound_role.py": 8.41,
    "tests/test_p4r152_one_page_one_answer.py": 0.32,
    "tests/test_p4r1_withdrawn_claims.py": 1.4,
    "tests/test_p4r24_advisory_remarks.py": 4.76,
    "tests/test_p4r34_form_census_per_level.py": 1.84,
    "tests/test_p4r53_recount_population.py": 2.81,
    "tests/test_p4r56_grid_separation.py": 1.36,
    "tests/test_p4r58_joined_numbers.py": 0.66,
    "tests/test_p4r59_unrepresentable_widths.py": 0.05,
    "tests/test_p4r60_hole_spellings.py": 0.31,
    "tests/test_p4r70_the_report_says_what_the_twin_carries.py": 0.44,
    "tests/test_p5r1_the_grain_clause_is_true.py": 0.97,
    "tests/test_pool_alone_marks.py": 180.57,
    "tests/test_pooled_number_scale.py": 3.18,
    "tests/test_pooled_scale_refusals.py": 8.04,
    "tests/test_profile_document.py": 8.93,
    "tests/test_profile_version_4.py": 1.16,
    "tests/test_profile_version_5.py": 1.54,
    "tests/test_provenance.py": 37.25,
    "tests/test_r5_trailing_delimiter_reading.py": 5.09,
    "tests/test_r6_taxonomy_contract.py": 59.23,
    "tests/test_r6f5_write_transaction.py": 0.01,
    "tests/test_reading.py": 6.71,
    "tests/test_reading_agreement.py": 9.92,
    "tests/test_reading_header_shape.py": 0.01,
    "tests/test_round2_disclosure.py": 43.78,
    "tests/test_round2_numbers_dates.py": 5.27,
    "tests/test_ruling_first_row_not_told.py": 2.32,
    "tests/test_ruling_identifier_prefix.py": 20.42,
    "tests/test_ruling_levels_counted_by_subtraction.py": 7.53,
    "tests/test_ruling_pooled_held_back_levels.py": 12.86,
    "tests/test_shipped_page_review.py": 3.39,
    "tests/test_stage2_dates_as_written.py": 35.13,
    "tests/test_stage2_datetime_oracle.py": 6.41,
    "tests/test_stage2_decimal_comma_readings.py": 0.44,
    "tests/test_stage2_grouping_oracle.py": 0.47,
    "tests/test_stage2_judged_provenance.py": 14.96,
    "tests/test_stage2_nested_grouping_loss.py": 1.3,
    "tests/test_stage2_refusals.py": 2.77,
    "tests/test_stage2_round_trip.py": 63.35,
    "tests/test_stage2_spellings_survive.py": 1.46,
    "tests/test_stage2_summary.py": 40.28,
    "tests/test_stage2_timestamp_spellings.py": 117.02,
    "tests/test_stage3_answer_paths.py": 2.9,
    "tests/test_stage3_default_floor.py": 39.09,
    "tests/test_stage3_gate.py": 155.99,
    "tests/test_stage3_review_dates.py": 8.78,
    "tests/test_stage3_review_numeric_robustness.py": 16.19,
    "tests/test_stage3_review_sentences.py": 2.66,
    "tests/test_stage3_tail_rule.py": 62.56,
    "tests/test_stage3b_base.py": 20.71,
    "tests/test_stage3b_clock.py": 92.53,
    "tests/test_stage3b_clock_review.py": 127.11,
    "tests/test_stage3b_count_pass_speed.py": 68.35,
    "tests/test_stage3b_count_room.py": 19.99,
    "tests/test_stage3b_counted.py": 213.21,
    "tests/test_stage3b_counted_codex.py": 71.62,
    "tests/test_stage3b_gate.py": 194.66,
    "tests/test_stage3b_hour.py": 124.4,
    "tests/test_stage3b_hour_review.py": 8.36,
    "tests/test_stage3b_layout.py": 32.3,
    "tests/test_stage3b_route2.py": 26.16,
    "tests/test_stage3b_shared_steps.py": 26.37,
    "tests/test_stage3b_weekday_moments.py": 78.96,
    "tests/test_stage3b_weekday_review.py": 295.32,
    "tests/test_stage3b_width.py": 122.91,
    "tests/test_stage4_allocator_walk.py": 18.04,
    "tests/test_stage4_sign_repairs.py": 18.92,
    "tests/test_stage4_tier2a.py": 88.39,
    "tests/test_summary_and_properties.py": 41.37,
    "tests/test_tail_back_solve_without_recursion.py": 14.72,
    "tests/test_taxonomy.py": 4.6,
    "tests/test_twin_golden.py": 5.64,
    "tests/test_u1u2_count_every_present_cell.py": 0.4,
    "tests/test_validate_lock.py": 1.25,
    "tests/test_validation.py": 56.51,
    "tests/test_version_reach.py": 8.94,
    "tests/test_window_agreement.py": 192.39,
    "tests/test_workbook_dates.py": 26.02,
    "tests/test_workbook_round_trip.py": 267.81,
}
