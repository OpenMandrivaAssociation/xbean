Name:           xbean
Version:        3.7
BuildArch:      noarch

Release:        7
Summary:        Java plugin based web server

Group:          Development/Java
License:        ASL 2.0
URL:            http://geronimo.apache.org/xbean/

# unfortunately no source/binary releases are being made lately, just
# tags in repos and binary releases in maven repositories
# svn export http://svn.apache.org/repos/asf/geronimo/xbean/tags/xbean-3.7
# tar caf xbean-3.7.tar.xz xbean-3.7
Source0:        xbean-%{version}.tar.xz
Source1:        xbean.depmap

Patch0:         pom-%{version}.patch

BuildRequires:  java-devel
BuildRequires:  apache-commons-beanutils
BuildRequires:  apache-commons-logging
BuildRequires:  mx4j
BuildRequires:  objectweb-asm
BuildRequires:  ant
BuildRequires:  qdox
BuildRequires:  slf4j
BuildRequires:  felix-osgi-core >= 1.4.0
BuildRequires:  maven-plugin-bundle
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-idea-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-surefire-maven-plugin
BuildRequires:  maven-site-plugin
BuildRequires:  maven-shade-plugin

Requires:       java
Requires:       objectweb-asm
Requires:       apache-commons-logging


%description
The goal of XBean project is to create a plugin based server
analogous to Eclipse being a plugin based IDE. XBean will be able to
discover, download and install server plugins from an Internet based
repository. In addition, we include support for multiple IoC systems,
support for running with no IoC system, JMX without JMX code,
lifecycle and class loader management, and a rock solid Spring
integration.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Development/Java
Requires:       jpackage-utils

%description    javadoc
%{summary}.

%prep
%setup -q
# build failing on this due to doxia-sitetools problems
rm src/site/site.xml

# removes dependency on springframework and prevents building of
# modules depending on it. If other modules are required,
# springframework will have to be brought in first
%patch0 -p1

# Fix dependency on xbean-asm-shaded to original objectweb-asm
sed -i 's/org.apache.xbean.asm/org.objectweb.asm/' \
    xbean-reflect/src/main/java/org/apache/xbean/recipe/XbeanAsmParameterNameLoader.java

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mvn-jpp -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven2.jpp.depmap.file="%{SOURCE1}" \
        install javadoc:aggregate


%install
# for every module we want to be built
for sub in bundleutils finder reflect naming classpath; do
    # install jar
    install -Dpm 644 %{name}-${sub}/target/%{name}-${sub}-%{version}.jar \
            $RPM_BUILD_ROOT/%{_javadir}/xbean/%{name}-${sub}.jar;

    # intall pom
    install -Dpm 644 %{name}-${sub}/pom.xml $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP.%{name}-%{name}-${sub}.pom

    # maven depmap
    %add_to_maven_depmap org.apache.xbean %{name}-${sub} %{version} JPP/%{name} %{name}-${sub}
done

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# parent pom
install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_mavenpomdir}/JPP.%{name}-main.pom
%add_to_maven_depmap org.apache.xbean %{name} %{version} JPP/%{name} main

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc LICENSE NOTICE
%{_mavenpomdir}/*.pom
%{_mavendepmapfragdir}/%{name}
%{_javadir}/%{name}

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE
%{_javadocdir}/%{name}

