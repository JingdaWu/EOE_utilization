from __future__ import annotations


TEXTS = {'zh': {'page_title': 'EOE - 数据中心利用率调优',
        'app_name': 'EOE - 数据中心利用率调优',
        'page_subtitle': '数据中心设备利用率与资源整合调优决策助手',
        'app_caption': 'Energy Optimization Engine · Utilization & Resource Optimization Module',
        'sidebar_title': 'EOE - 数据中心利用率调优',
        'sidebar_desc': '数据中心设备利用率与资源整合调优决策助手',
        'language_toggle': 'English',
        'chip_utilization': '数据中心设备利用率分析',
        'chip_zombie': '闲置设备识别',
        'chip_consolidation': '设备整合决策助手',
        'chip_energy_saving': '设备整合经济性分析',
        'section_data': '设备数据上传',
        'section_data_desc': '上传数据中心资产利用率 CSV 文件',
        'section_model': '分析模式',
        'section_model_desc': '选择基础、进阶或高级分析模式',
        'section_threshold': '评估阈值定义',
        'section_threshold_desc': '输入低利用率、闲置设备的评判标准',
        'section_power': '功率与电价输入',
        'section_power_desc': '输入数据中心的功率消耗及加权平均电价',
        'section_consolidation': '整合条件设定',
        'section_consolidation_desc': '设定设备整合相关需求参数与限制条件',
        'section_advanced': '高级参数',
        'section_advanced_desc': '输入高级模式下用于分析评估的参数',
        'upload_file': '上传CSV',
        'uploaded_file_label': '点击下方按钮上传',
        'uploaded_file_help': '支持数据中心利用率日志CSV文档。文档中需至少包含timestamp、asset_id、utilization三列。',
        'download_template': '下载模板',
        'no_data': '请先上传数据中心利用率日志CSV。',
        'file_error': '数据中心利用率日志读取失败，请检查字段和格式',
        'value_uploaded': '已上传',
        'value_not_uploaded': '未上传',
        'analysis_mode': '分析模式',
        'mode_basic': '基础分析模式',
        'mode_standard': '进阶分析模式',
        'mode_enhanced': '高级分析模式',
        'mode_basic_help': '基础模式仅使用利用率、统一功率和阈值规则开展分析，适合小数据样本输入与快速初筛',
        'mode_standard_help': '进阶模式将结合设备目标整合比例、目标利用率和冷却收益开展，用于评估设备整合收益',
        'mode_enhanced_help': '高级模式将结合增加内存、IO、业务保护、可迁移性、迁移成本情景和风险评分开展全面收益分析',
        'low_util_threshold': '低利用率阈值标准（%）',
        'high_util_threshold': '活跃利用率阈值标准（%）',
        'high_duty_threshold': '活跃利用率时段占比阈值标准（%）',
        'idle_power': '默认空闲功率（W）（仅在利用率日志中数据缺失时生效）',
        'peak_power': '默认满载功率（W）（仅在利用率日志中数据缺失时生效）',
        'electricity_price': '加权平均电价（¥/kWh）',
        'consolidation_ratio': '候选设备整合比例（%）',
        'safe_util_limit': '整合后利用率上限阈值（%）',
        'cooling_factor': '冷却系数',
        'migration_cost_multiplier': '设备整合迁移成本系数',
        'risk_cost_multiplier': '设备整合风险成本系数',
        'run_hint': '请核对是否完成全部数据与参数输入',
        'run_button_new': '开始利用率调优分析评估',
        'analysis_done': '分析完成',
        'simulation_failed': '分析失败',
        'input_error': '输入错误',
        'empty_title': '数据中心设备利用率与资源调优分析流程指南',
        'empty_body': '请先在左侧输入栏依次完成：1）利用率日志上传；2）分析模式选择；3）分析评估所需各项阈值参数设置。完成所需各项数据和参数上传后点击“开始利用率调优分析评估”。如果部分数据或参数缺失，可以下载模板csv文档填写或使用样品数据进行试用。',
        'scenario_summary': '分析模式及数据输入状态摘要',
        'label_mode': '分析模式',
        'label_data_status': '数据上传状态',
        'label_price': '加权平均电价（¥/kWh）',
        'label_period': '分析周期',
        'label_assets': '资产数量',
        'model_notice_title': '分析模式选用模型说明',
        'basic_notice': '基础模式仅使用利用率、统一功率和阈值规则开展分析，适合小数据样本输入与快速初筛。此模式重点评估优设备利用状态，不直接给出整合建议和经济性分析结论',
        'standard_notice': '进阶模式会结合设备目标整合比例、目标利用率和冷却收益开展，用于评估设备整合收益，估算电费节省比例、年运营成本节省数额和净收益',
        'enhanced_notice': '高级模式将在进阶模式的功能基础上结合增加内存、IO、业务保护、可迁移性、迁移成本情景和风险评分开展更高精度的收益分析与决策建议',
        'key_metrics': '核心指标',
        'kpi_desc': '下方展示的核心指标包括设备利用率状态及整合经济性相关的各类经济性指标。',
        'total_assets': '设备总数',
        'low_util_assets': '低利用率设备数量',
        'zombie_assets': '疑似闲置设备数量',
        'candidate_assets': '评估可整合设备',
        'total_energy': '周期总耗电量',
        'waste_energy': '潜在浪费电量',
        'gross_saving': '年运营经济性节省收益',
        'net_saving': '首年净收益',
        'annual_net_saving': '首年净收益',
        'shutdown_assets': '评估可下线设备数量',
        'post_utilization': '整合后平均利用率',
        'top_waste_group': '主要浪费分组',
        'results_title': '结果概览',
        'current_asset_status': '当前资产状态',
        'consolidation_result': '整合测算结果',
        'economic_result': '经济性结果',
        'charts_title': '图表分析',
        'chart_util_distribution': '资产平均利用率分布',
        'chart_energy_scatter': '平均利用率 - 耗电量散点图',
        'chart_group_energy': '分组能耗与浪费成本',
        'chart_zombie_top': '疑似闲置设备节省潜力 Top 10',
        'chart_saving_waterfall': '年度节省与首年净收益拆解',
        'chart_action_category': '管理动作分类',
        'chart_hourly_load': '利用率日志周期内功率消耗时间序列矩阵',
        'x_util': '平均利用率 %',
        'x_energy': '耗电量 kWh',
        'x_group': '分组',
        'x_asset': '资产',
        'x_time': '时间',
        'y_count': '资产数量',
        'y_energy': '能耗 kWh',
        'y_cost': '费用 ¥',
        'y_power': '功率 kW',
        'risk_score': '整合优先级评分',
        'detailed_tables': '详细数据表',
        'detailed_tables_hint': '以下表格主要用于工程核查和结果追溯',
        'table_title': '资产分析清单',
        'priority_table_title': '优先排查清单',
        'group_table_title': '分组分析清单',
        'type_table_title': '资产类型分析清单',
        'action_table_title': '管理动作汇总',
        'asset_id': '资产 ID',
        'asset_type': '资产类型',
        'group': '分组',
        'avg_utilization': '平均利用率 %',
        'max_utilization': '峰值利用率 %',
        'p95_utilization': 'P95 利用率 %',
        'high_load_duty': '活跃时段占比 %',
        'avg_memory_utilization': '平均内存利用率 %',
        'avg_disk_io': '平均磁盘 IO %',
        'avg_network_io': '平均网络 IO %',
        'avg_power_kw': '平均功率 kW',
        'energy_kwh': '耗电量 kWh',
        'cost': '电费 ¥',
        'waste_energy_kwh': '潜在浪费电量 kWh',
        'waste_cost': '潜在浪费电费 ¥',
        'is_low_util': '低利用率',
        'is_zombie': '疑似闲置',
        'is_business_protected': '业务保护',
        'is_migratable': '可迁移',
        'priority_level': '优先级',
        'action_category': '建议动作',
        'selected_for_shutdown_assessment': '纳入下线评估',
        'estimated_shutdown': '理论可下线数量',
        'post_avg_utilization': '整合后平均利用率 %',
        'saving_energy_kwh': '可节省电量 kWh',
        'saving_cost': '设备侧节省 ¥',
        'cooling_saving_kwh': '冷却联动节省 kWh',
        'cooling_saving_cost': '冷却侧节省 ¥',
        'migration_cost': '迁移成本 ¥',
        'restart_risk_cost': '重启风险成本 ¥',
        'gross_saving_cost': '年度运营节省 ¥',
        'net_saving_cost': '首年净收益 ¥',
        'annual_net_saving_col': '首年净收益 ¥',
        'report_title': '设备利用率、设备整合与经济性收益分析报告',
        'report_desc': '分析报告内容根据当前所选分析模式侧重有所不同：基础模式聚焦设备利用率可视化，进阶模式额外包含设备整合决策建议及整合经济性分析，高级模式在进阶模式的基础上额外增加了精度相关参数的考察权重',
        'report_empty': '暂无可显示的分析报告',
        'summary_tab': '概括摘要',
        'economic_tab': '经济性分析',
        'decision_tab': '设备整合决策建议',
        'risk_tab': '风险提示',
        'summary_title': '摘要结论',
        'economic_title': '经济性结论',
        'decision_title': '管理建议',
        'risk_title': '风险提示',
        'advanced_title': '关键洞察',
        'template_filename': 'sample_utilization_template.csv',
        'currency': '¥',
        'kwh': 'kWh',
        'kw': 'kW',
        'days': '天',
        'assets_unit': '台',
        'percent': '%',
        'yes': '是',
        'no': '否',
        'energy_waste_result': '能耗浪费识别',
        'priority_review_result': '优先排查结果',
        'risk_decision_result': '风险与决策',
        'low_util_ratio': '低利用率资产占比',
        'zombie_ratio': '疑似闲置设备占比',
        'protected_assets': '业务保护资产',
        'baseline_cost': '整合前电费基准 ¥',
        'post_consolidation_cost': '整合后估算电费 ¥',
        'cost_saving_ratio': '设备整合前后电费节省比率',
        'annual_operating_saving': '年运营电费节省数额',
        'one_time_consolidation_cost': '设备整合成本',
        'first_year_net_benefit': '首年净收益金额',
        'chart_asset_status_pie': '设备利用率状态比例图',
        'asset_status_normal': '高利用率设备',
        'asset_status_low_util': '低利用率设备',
        'asset_status_zombie': '疑似闲置设备',
        'chart_cost_saving_pie': '设备整合前后电费节省比率图',
        'annual_remaining_cost': '整合后年度支出电费',
        'chart_annual_economics_bar': '设备整合后年度经济性收益'},
 'en': {
        'page_title': 'EOE - Data Center Utilization Optimization',  # refined EN wording
        'app_name': 'EOE - Data Center Utilization Optimization',  # refined EN wording
        'page_subtitle': 'A decision-support dashboard for data center utilization screening, idle-resource review, and consolidation economics.',  # refined EN wording
        'app_caption': 'Energy Optimization Engine · Utilization & Resource Optimization Module',
        'sidebar_title': 'EOE - Data Center Utilization Optimization',  # refined EN wording
        'sidebar_desc': 'Upload utilization logs and configure screening, consolidation, and cost assumptions.',  # refined EN wording
        'language_toggle': '中文',
        'chip_utilization': 'Utilization Assessment',  # refined EN wording
        'chip_zombie': 'Idle / Zombie Asset Review',  # refined EN wording
        'chip_consolidation': 'Resource Consolidation Review',  # refined EN wording
        'chip_energy_saving': 'Consolidation Economics',  # refined EN wording
        'section_data': 'Utilization Data Upload',  # refined EN wording
        'section_data_desc': 'Upload a data center asset utilization CSV file.',  # refined EN wording
        'section_model': 'Analysis Mode',
        'section_model_desc': 'Choose Basic, Standard, or Enhanced Mode according to available data and decision depth.',  # refined EN wording
        'section_threshold': 'Screening Thresholds',  # refined EN wording
        'section_threshold_desc': 'Define the criteria for low-utilization and potentially idle assets.',  # refined EN wording
        'section_power': 'Power and Electricity Price',  # refined EN wording
        'section_power_desc': 'Set default power assumptions and weighted average electricity price.',  # refined EN wording
        'section_consolidation': 'Consolidation Assumptions',  # refined EN wording
        'section_consolidation_desc': 'Set consolidation ratio, target utilization limit, and cooling-saving conversion factor.',  # refined EN wording
        'section_advanced': 'Enhanced-mode Parameters',  # refined EN wording
        'section_advanced_desc': 'Configure scenario factors used for enhanced risk and cost assessment.',  # refined EN wording
        'upload_file': 'Upload CSV',
        'uploaded_file_label': 'Click below to upload',  # refined EN wording
        'uploaded_file_help': 'Upload a data center utilization log in CSV format. Required columns: timestamp, asset_id, utilization.',  # refined EN wording
        'download_template': 'Download Template',  # refined EN wording
        'no_data': 'Please upload a data center utilization log CSV first.',  # refined EN wording
        'file_error': 'Failed to read the utilization log. Please check the required columns and file format.',  # refined EN wording
        'value_uploaded': 'Uploaded',
        'value_not_uploaded': 'Not Uploaded',
        'analysis_mode': 'Analysis Mode',
        'mode_basic': 'Basic Mode',  # refined EN wording
        'mode_standard': 'Standard Mode',  # refined EN wording
        'mode_enhanced': 'Enhanced Mode',  # refined EN wording
        'mode_basic_help': 'Uses utilization data, uniform power assumptions, and threshold rules for quick preliminary screening.',  # refined EN wording
        'mode_standard_help': 'Adds consolidation ratio, target utilization limit, and cooling-saving assumptions to estimate consolidation economics.',  # refined EN wording
        'mode_enhanced_help': 'Adds memory, IO, business protection, migratability, migration-cost scenarios, and risk-cost scenarios for a more conservative assessment.',  # refined EN wording
        'low_util_threshold': 'Low-utilization Threshold (%)',  # refined EN wording
        'high_util_threshold': 'Active-utilization Threshold (%)',  # refined EN wording
        'high_duty_threshold': 'Active-time Share Threshold (%)',  # refined EN wording
        'idle_power': 'Default Idle Power (W) — used only when missing from the log',  # refined EN wording
        'peak_power': 'Default Full-load Power (W) — used only when missing from the log',  # refined EN wording
        'electricity_price': 'Weighted Average Electricity Price (¥/kWh)',  # refined EN wording
        'consolidation_ratio': 'Candidate Asset Consolidation Ratio (%)',  # refined EN wording
        'safe_util_limit': 'Post-consolidation Utilization Limit (%)',  # refined EN wording
        'cooling_factor': 'Cooling-saving Conversion Factor',  # refined EN wording
        'migration_cost_multiplier': 'Consolidation Migration-cost Factor',  # refined EN wording
        'risk_cost_multiplier': 'Consolidation Risk-cost Factor',  # refined EN wording
        'run_hint': 'Please confirm that all required data and parameters have been entered.',  # refined EN wording
        'run_button_new': 'Run Utilization Optimization Assessment',  # refined EN wording
        'analysis_done': 'Analysis completed.',
        'simulation_failed': 'Analysis failed',
        'input_error': 'Input error',
        'empty_title': 'Data Center Utilization and Resource Optimization Workflow',  # refined EN wording
        'empty_body': 'Complete the workflow in the left sidebar: 1) upload a utilization log; 2) select an analysis mode; 3) configure the required thresholds and assumptions. Then click “Run Utilization Optimization Assessment”. If data is missing, download the CSV template and fill in a compatible sample.',  # refined EN wording
        'scenario_summary': 'Analysis Mode and Data Input Summary',  # refined EN wording
        'label_mode': 'Analysis Mode',
        'label_data_status': 'Data Upload Status',  # refined EN wording
        'label_price': 'Weighted Average Electricity Price (¥/kWh)',  # refined EN wording
        'label_period': 'Analysis Period',
        'label_assets': 'Asset Count',
        'model_notice_title': 'Analysis-mode Methodology Notes',  # refined EN wording
        'basic_notice': 'Basic Mode uses utilization data, uniform power assumptions, and threshold rules for quick screening. It focuses on utilization status and priority review targets, without generating consolidation economics.',  # refined EN wording
        'standard_notice': 'Standard Mode adds consolidation ratio, target utilization limit, and cooling-saving assumptions to estimate electricity cost saving ratio, annual operating saving, and first-year net benefit.',  # refined EN wording
        'enhanced_notice': 'Enhanced Mode further incorporates memory utilization, IO signals, business protection, migratability, migration-cost scenarios, and risk scoring to support a more conservative assessment.',  # refined EN wording
        'key_metrics': 'Key Metrics',
        'kpi_desc': 'The metrics below summarize utilization status, consolidation potential, and mode-specific economic indicators.',  # refined EN wording
        'total_assets': 'Total Devices / Assets',  # refined EN wording
        'low_util_assets': 'Low-utilization Devices',  # refined EN wording
        'zombie_assets': 'Suspected Idle Assets',  # refined EN wording
        'candidate_assets': 'Consolidation-review Candidates',  # refined EN wording
        'total_energy': 'Sample-period Energy Consumption',  # refined EN wording
        'waste_energy': 'Potential Waste Energy',  # refined EN wording
        'gross_saving': 'Annual Operating Saving',  # refined EN wording
        'net_saving': 'First-year Net Benefit',  # refined EN wording
        'annual_net_saving': 'First-year Net Benefit',  # refined EN wording
        'shutdown_assets': 'Assets Flagged for Shutdown / Migration Review',  # refined EN wording
        'post_utilization': 'Post-consolidation Average Utilization',  # refined EN wording
        'top_waste_group': 'Largest Waste-contribution Group',  # refined EN wording
        'results_title': 'Results Overview',
        'current_asset_status': 'Current Asset Status',  # refined EN wording
        'consolidation_result': 'Consolidation Assessment',  # refined EN wording
        'economic_result': 'Economic Results',  # refined EN wording
        'charts_title': 'Chart Analysis',  # refined EN wording
        'chart_util_distribution': 'Average Utilization Distribution',
        'chart_energy_scatter': 'Average Utilization vs. Energy Consumption',
        'chart_group_energy': 'Energy Use and Waste Cost by Group',  # refined EN wording
        'chart_zombie_top': 'Top 10 Suspected Idle Assets by Saving Potential',  # refined EN wording
        'chart_saving_waterfall': 'Annual Saving and First-year Net Benefit Breakdown',  # refined EN wording
        'chart_action_category': 'Recommended Management Actions',  # refined EN wording
        'chart_hourly_load': 'Power Consumption Time Series for the Utilization-log Period',  # refined EN wording
        'x_util': 'Average Utilization (%)',  # refined EN wording
        'x_energy': 'Energy (kWh)',  # refined EN wording
        'x_group': 'Group',
        'x_asset': 'Asset',
        'x_time': 'Time',
        'y_count': 'Asset Count',
        'y_energy': 'Energy (kWh)',  # refined EN wording
        'y_cost': 'Cost (¥)',  # refined EN wording
        'y_power': 'Power (kW)',  # refined EN wording
        'risk_score': 'Consolidation Priority Score',  # refined EN wording
        'detailed_tables': 'Detailed Data Tables',
        'detailed_tables_hint': 'The following tables are intended for engineering review and result traceability.',  # refined EN wording
        'table_title': 'Asset Analysis List',
        'priority_table_title': 'Priority Review List',  # refined EN wording
        'group_table_title': 'Group Analysis List',
        'type_table_title': 'Asset Type Analysis List',
        'action_table_title': 'Management Action Summary',
        'asset_id': 'Asset ID',
        'asset_type': 'Asset Type',
        'group': 'Group',
        'avg_utilization': 'Average Utilization (%)',  # refined EN wording
        'max_utilization': 'Peak Utilization (%)',  # refined EN wording
        'p95_utilization': 'P95 Utilization (%)',  # refined EN wording
        'high_load_duty': 'Active-time Share (%)',  # refined EN wording
        'avg_memory_utilization': 'Average Memory Utilization (%)',  # refined EN wording
        'avg_disk_io': 'Average Disk IO (%)',  # refined EN wording
        'avg_network_io': 'Average Network IO (%)',  # refined EN wording
        'avg_power_kw': 'Average Power (kW)',  # refined EN wording
        'energy_kwh': 'Energy Consumption (kWh)',  # refined EN wording
        'cost': 'Electricity Cost (¥)',  # refined EN wording
        'waste_energy_kwh': 'Potential Waste Energy (kWh)',  # refined EN wording
        'waste_cost': 'Potential Waste Cost (¥)',  # refined EN wording
        'is_low_util': 'Low-utilization',
        'is_zombie': 'Suspected Idle / Zombie',  # refined EN wording
        'is_business_protected': 'Business-protected',  # refined EN wording
        'is_migratable': 'Migratable',
        'priority_level': 'Priority Level',
        'action_category': 'Recommended Action',  # refined EN wording
        'selected_for_shutdown_assessment': 'Included in Shutdown / Migration Review',  # refined EN wording
        'estimated_shutdown': 'Estimated Shutdown / Migration-review Count',  # refined EN wording
        'post_avg_utilization': 'Post-consolidation Average Utilization (%)',  # refined EN wording
        'saving_energy_kwh': 'Avoidable Energy Consumption (kWh)',  # refined EN wording
        'saving_cost': 'IT-side Electricity Saving (¥)',  # refined EN wording
        'cooling_saving_kwh': 'Cooling-linked Energy Saving (kWh)',  # refined EN wording
        'cooling_saving_cost': 'Cooling-side Electricity Saving (¥)',  # refined EN wording
        'migration_cost': 'Migration Cost (¥)',  # refined EN wording
        'restart_risk_cost': 'Restart / Business Risk Cost (¥)',  # refined EN wording
        'gross_saving_cost': 'Annual Operating Saving (¥)',  # refined EN wording
        'net_saving_cost': 'First-year Net Benefit (¥)',  # refined EN wording
        'annual_net_saving_col': 'First-year Net Benefit (¥)',  # refined EN wording
        'report_title': 'Equipment Utilization, Consolidation, and Economic-benefit Analysis Report',  # refined EN wording
        'report_desc': 'Report content is mode-aware: Basic Mode focuses on utilization screening, Standard Mode adds consolidation economics, and Enhanced Mode adds risk and business-constraint filtering.',  # refined EN wording
        'report_empty': 'No report content is available.',
        'summary_tab': 'Summary',
        'economic_tab': 'Economics',
        'decision_tab': 'Consolidation Recommendations',  # refined EN wording
        'risk_tab': 'Risk Notes',  # refined EN wording
        'summary_title': 'Executive Summary',  # refined EN wording
        'economic_title': 'Economic Conclusions',  # refined EN wording
        'decision_title': 'Management Recommendations',  # refined EN wording
        'risk_title': 'Risk Notes',  # refined EN wording
        'advanced_title': 'Key Insights',
        'template_filename': 'sample_utilization_template.csv',
        'currency': '¥',
        'kwh': 'kWh',
        'kw': 'kW',
        'days': 'days',
        'assets_unit': 'assets',
        'percent': '%',
        'yes': 'Yes',
        'no': 'No',
        'energy_waste_result': 'Energy-waste Identification',  # refined EN wording
        'priority_review_result': 'Priority Review Results',  # refined EN wording
        'risk_decision_result': 'Risk and Decision Support',  # refined EN wording
        'low_util_ratio': 'Low-utilization Asset Share',  # refined EN wording
        'zombie_ratio': 'Suspected Idle-asset Share',  # refined EN wording
        'protected_assets': 'Business-protected Assets',  # refined EN wording
        'baseline_cost': 'Baseline Electricity Cost (¥)',  # refined EN wording
        'post_consolidation_cost': 'Estimated Post-consolidation Electricity Cost (¥)',  # refined EN wording
        'cost_saving_ratio': 'Electricity Cost Saving Ratio',  # refined EN wording
        'annual_operating_saving': 'Annual Operating Saving',  # refined EN wording
        'one_time_consolidation_cost': 'One-time Consolidation Cost',  # refined EN wording
        'first_year_net_benefit': 'First-year Net Benefit',  # refined EN wording
        'chart_asset_status_pie': 'Device Utilization Status Share',  # refined EN wording
        'asset_status_normal': 'Normal / Higher-utilization Devices',  # refined EN wording
        'asset_status_low_util': 'Low-utilization Devices',  # refined EN wording
        'asset_status_zombie': 'Suspected Idle Devices',  # refined EN wording
        'chart_cost_saving_pie': 'Electricity Cost Saving Ratio after Consolidation',  # refined EN wording
        'annual_remaining_cost': 'Remaining Annual Electricity Cost',  # refined EN wording
        'chart_annual_economics_bar': 'Annualized Economic Benefit after Consolidation'  # refined EN wording
    }}


def get_text(language: str) -> dict:
    return TEXTS.get(language, TEXTS["en"])
